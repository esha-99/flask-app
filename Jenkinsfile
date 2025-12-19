pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "eshashamraiz2004/flask-app"
        DOCKER_TAG   = "${BUILD_NUMBER}"
        DOCKERHUB_CREDENTIALS = 'dockerhub-credentials' // DockerHub credentials ID in Jenkins
        APP_PORT = "5001" // External port for EC2
    }

    stages {
        stage('Checkout SCM') {
            steps {
                echo "Checking out code from Git..."
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image ${DOCKER_IMAGE}:${DOCKER_TAG}..."
                    sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                }
            }
        }

        stage('Run Docker Container') {
            steps {
                script {
                    echo "Running Docker container on port ${APP_PORT}..."
                    // Remove existing container if present
                    sh """
                        if [ \$(docker ps -a -q -f name=flask-app) ]; then
                            docker rm -f flask-app
                        fi
                        docker run -d --name flask-app -p ${APP_PORT}:5000 ${DOCKER_IMAGE}:${DOCKER_TAG}
                    """
                }
            }
        }

        stage('Wait for App to Start') {
            steps {
                script {
                    echo "Waiting for Flask app to start..."
                    // Simple wait, you can improve with health check
                    sh "sleep 10"
                }
            }
        }

        stage('OWASP ZAP Ready for Scan') {
            steps {
                echo "Container is running on port ${APP_PORT}. You can now scan it using OWASP ZAP CLI or GUI."
                echo "Example ZAP scan command:"
                echo "zap-cli quick-scan --self-contained --start-options '-config api.disablekey=true' http://localhost:${APP_PORT}"
            }
        }

        stage('Push to DockerHub') {
            steps {
                script {
                    echo "Logging in and pushing image to DockerHub..."
                    withDockerRegistry([credentialsId: "${DOCKERHUB_CREDENTIALS}", url: ""]) {
                        sh "docker push ${DOCKER_IMAGE}:${DOCKER_TAG}"
                    }
                }
            }
        }
    }

    post {
        always {
            echo "Cleaning up workspace and stopping container..."
            sh """
                if [ \$(docker ps -a -q -f name=flask-app) ]; then
                    docker rm -f flask-app
                fi
            """
            cleanWs()
        }
        success {
            echo "✅ Pipeline completed successfully!"
        }
        failure {
            echo "❌ Pipeline failed!"
        }
    }
}
