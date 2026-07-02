pipeline {
    agent any
    
    environment {
        // Must match the global tool name you created in Jenkins (Manage Jenkins -> Tools)
        SCANNER_HOME = tool 'sonar-scanner'
        
        APP_NAME     = "devsecops-api"
        RELEASE      = "1.0"
        DOCKER_USER  = "naman96"
        DOCKER_PASS  = 'docker-cred' // The ID of your Jenkins DockerHub credentials string
        IMAGE_NAME   = "${DOCKER_USER}/${APP_NAME}"
        IMAGE_TAG    = "${RELEASE}-${BUILD_NUMBER}"
    }

    stages {
        stage('1. Cleanup Workspace') {
            steps {
                cleanWs()
            }
        }
        
        stage('2. SCM Checkout') {
            steps {
                // Pulls dynamically from whatever repository triggered the job
                checkout scm
            }
        }
        
        stage('3. File System Scan: Trivy') {
            steps {
                script {
                    echo 'Scanning repository source files for misconfigurations and exposed secrets...'
                    sh 'trivy fs --format table -o trivy-file-scan-report.html .'
                }
            }
        }
        
        stage('4. Static Code Analysis: SonarQube') {
            steps {
                script {
                    // Must match the system server profile name inside Manage Jenkins -> System
                    withSonarQubeEnv('sonarqube-server') {
                        sh """${SCANNER_HOME}/bin/sonar-scanner \
                            -Dsonar.projectName=${APP_NAME} \
                            -Dsonar.projectKey=${APP_NAME} \
                            -Dsonar.sources=app/ \
                            -Dsonar.language=py"""
                    }
                }
            }
        }
        
        stage('5. Quality Gate Check: SonarQube') {
            steps {
                script {
                    echo 'Waiting for SonarQube analysis platform callback response...'
                    // Aborts pipeline if code quality standards or security vulnerabilities fail thresholds
                    waitForQualityGate abortPipeline: true, credentialsId: 'sonar-token'
                }
            }
        }
        
        stage('6. Docker Image Build') {
            steps {
                script {
                    echo 'Compiling multi-stage Dockerfile into hardened production runtime image...'
                    docker_image = docker.build("${IMAGE_NAME}:${IMAGE_TAG}")
                }
            }
        }
        
        stage('7. Docker Image Scan: Trivy') {
            steps {
                script {
                    echo 'Scanning final container layer filesystems for known OS vulnerabilities...'
                    sh "trivy image --format table -o trivy-docker-scan-report.html ${IMAGE_NAME}:${IMAGE_TAG}"
                }
            }
        }
        
        stage('8. Docker Image Push: DockerHub') {
            steps {
                script {
                    // Authenticates securely using internal Jenkins credential store IDs
                    docker.withRegistry('', DOCKER_PASS) {
                        docker_image.push("${IMAGE_TAG}")
                        docker_image.push('latest')
                    }
                }
            }
        }
        
        stage('9. Post-Build Infrastructure Cleanup') {
            steps {
                script {
                    echo 'Purging temporary build local images to save VM host disk capacity...'
                    sh "docker rmi ${IMAGE_NAME}:${IMAGE_TAG}"
                    sh "docker rmi ${IMAGE_NAME}:latest"
                }
            }
        }
    }
    
    post {
        always {
            script {
                def jobName        = env.JOB_NAME
                def buildNumber    = env.BUILD_NUMBER
                def pipelineStatus = currentBuild.result ?: 'SUCCESS'
                def bannerColor    = pipelineStatus.toUpperCase() == 'SUCCESS' ? 'green' : 'red'
                
                def body = """
                    <html>
                        <body>
                            <div style="border: 4px solid ${bannerColor}; padding: 10px;">
                                <h2>${jobName} - Build ${buildNumber}</h2>
                                <div style="background-color: ${bannerColor}; padding: 10px;">
                                    <h3 style="color: white;">Pipeline Status: ${pipelineStatus.toUpperCase()}</h3>
                                </div>
                                <p>Check the detailed pipeline metrics <a href="${BUILD_URL}">here inside the console output</a>.</p>
                            </div>
                        </body>
                    </html>"""
                
                emailext (
                    subject: "${jobName} - Build ${buildNumber} - ${pipelineStatus.toUpperCase()}",
                    body: body,
                    to: 'itsmenaman06@gmail.com',
                    from: 'jenkins@example.com',
                    replyTo: 'jenkins@example.com',
                    mimeType: 'text/html',
                    attachmentsPattern: 'trivy-file-scan-report.html, trivy-docker-scan-report.html'
                )
            }
        }
    }
}
