pipeline {
    agent any
    
    environment {
        // Must match the tool name configured in Manage Jenkins -> Tools
        SCANNER_HOME = tool 'sonar-scanner'
        
        APP_NAME     = "devsecops-api"
        RELEASE      = "1.0"
        DOCKER_USER  = "naman96"
        DOCKER_PASS  = 'docker-cred' // Internal Jenkins Credentials ID for DockerHub
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
        
        stage('4. Static Code Analysis: SonarQube') {
            steps {
                script {
                    echo 'Injecting code artifacts into SonarQube server...'
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
                    echo 'Awaiting webhook callback notification from SonarQube server...'
                    waitForQualityGate abortPipeline: true, credentialsId: 'sonar-token'
                }
            }
        }
        
        stage('6. Docker Image Build') {
            steps {
                script {
                    echo 'Compiling multi-stage Dockerfile into production runtime image...'
                    docker_image = docker.build("${IMAGE_NAME}:${IMAGE_TAG}")
                }
            }
        }
        
        stage('7. Docker Image Scan: Trivy') {
            steps {
                script {
                    echo 'Auditing final container layer file system binary footprints for vulnerabilities...'
                    sh "trivy image --format table -o trivy-docker-scan-report.html ${IMAGE_NAME}:${IMAGE_TAG}"
                }
            }
        }
        
        stage('8. Docker Image Push: DockerHub') {
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
        
        stage('9. Post-Build Infrastructure Cleanup') {
            steps {
                script {
                    echo 'Purging temporary build images to preserve host disk capacity...'
                    sh "docker rmi ${IMAGE_NAME}:${IMAGE_TAG}"
                    sh "docker rmi ${IMAGE_NAME}:latest"
                }
            }
        }
    }
}
