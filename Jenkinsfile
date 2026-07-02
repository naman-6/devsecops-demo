pipeline {
    agent any
    
    environment {
        // Must match the tool name you configured in Manage Jenkins -> Tools
        SCANNER_HOME = tool 'sonar-scanner'
        
        APP_NAME     = "devsecops-api"
        RELEASE      = "1.0"
        DOCKER_USER  = "naman96"
        DOCKER_PASS  = 'docker-cred' // Must match the internal Jenkins Credentials ID for DockerHub
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
                // Dynamically checks out the branch that triggered the SCM poll
                checkout scm
            }
        }
        
        stage('3. File System Scan: Trivy') {
            steps {
                script {
                    echo 'Scanning repository workspace for misconfigurations and exposed secrets...'
                    sh 'trivy fs --format table -o trivy-file-scan-report.html .'
                }
            }
        }
        
        stage('4. Run Unit Tests & Coverage') {
            steps {
                script {
                    echo 'Launching isolated Python container to execute pytest suite...'
                    // DevSecOps Best Practice: Run tests inside an ephemeral container 
                    // to prevent toolchain contamination on the host/Jenkins master.
                    sh '''
                        docker run --rm \
                        -v ${WORKSPACE}:/workspace \
                        -w /workspace \
                        python:3.11-slim \
                        sh -c "pip install --no-cache-dir -r app/requirements.txt && pytest --cov=app --cov-report=xml:coverage.xml"
                    '''
                    echo 'Unit tests executed and coverage.xml report successfully generated!'
                }
            }
        }
        
        stage('5. Static Code Analysis: SonarQube') {
            steps {
                script {
                    echo 'Injecting code artifacts and coverage analytics into SonarQube...'
                    // Must match the system server profile name inside Manage Jenkins -> System
                    withSonarQubeEnv('sonarqube-server') {
                        sh """${SCANNER_HOME}/bin/sonar-scanner \
                            -Dsonar.projectName=${APP_NAME} \
                            -Dsonar.projectKey=${APP_NAME} \
                            -Dsonar.sources=app/ \
                            -Dsonar.language=py \
                            -Dsonar.python.coverage.reportPaths=coverage.xml"""
                    }
                }
            }
        }
        
        stage('6. Quality Gate Check: SonarQube') {
            steps {
                script {
                    echo 'Awaiting webhook callback notification from SonarQube server...'
                    // Hardened Security Control: Aborts pipeline instantly if code fails quality thresholds
                    waitForQualityGate abortPipeline: true, credentialsId: 'sonar-token'
                }
            }
        }
        
        stage('7. Docker Image Build') {
            steps {
                script {
                    echo 'Compiling multi-stage Dockerfile into production-hardened runtime image...'
                    docker_image = docker.build("${IMAGE_NAME}:${IMAGE_TAG}")
                }
            }
        }
        
        stage('8. Docker Image Scan: Trivy') {
            steps {
                script {
                    echo 'Auditing final container layer file system binary footprints for vulnerabilities...'
                    sh "trivy image --format table -o trivy-docker-scan-report.html ${IMAGE_NAME}:${IMAGE_TAG}"
                }
            }
        }
        
        stage('9. Docker Image Push: DockerHub') {
            steps {
                script {
                    echo 'Authenticating registry transaction and publishing images to DockerHub...'
                    docker.withRegistry('', DOCKER_PASS) {
                        docker_image.push("${IMAGE_TAG}")
                        docker_image.push('latest')
                    }
                }
            }
        }
        
        stage('10. Post-Build Infrastructure Cleanup') {
            steps {
                script {
                    echo 'Purging temporary build images to preserve host disk capacity...'
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
                        <body style="font-family: Arial, sans-serif;">
                            <div style="border: 4px solid ${bannerColor}; padding: 15px; border-radius: 5px;">
                                <h2 style="color: #333;">${jobName} - Build #${buildNumber}</h2>
                                <div style="background-color: ${bannerColor}; padding: 10px; margin-bottom: 15px;">
                                    <h3 style="color: white; margin: 0;">Pipeline Execution Result: ${pipelineStatus.toUpperCase()}</h3>
                                </div>
                                <p>The DevSecOps pipeline compilation has concluded. You can review detailed console trace transcripts and metrics directly inside the automation environment interface.</p>
                                <p>Access explicit build pathing logs: <a href="${BUILD_URL}">Console Output Link</a></p>
                            </div>
                        </body>
                    </html>"""
                
                echo 'Dispatching consolidated artifact status telemetry report to security engineering distributions...'
                emailext (
                    subject: "${jobName} - Build #${buildNumber} - ${pipelineStatus.toUpperCase()}",
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
