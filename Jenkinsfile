pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "eshashamraiz2004/flask-app"
        DOCKER_TAG   = "${BUILD_NUMBER}"
        DOCKERHUB_CREDENTIALS = 'dockerhub-credentials'
        APP_PORT = "5001"
    }

    stages {
        stage('Checkout SCM') {
            steps {
                echo "Checking out code from Git..."
                checkout scm
            }
        }

        stage('Build and Run Docker Container') {
            steps {
                script {
                    echo "Building Docker image ${DOCKER_IMAGE}:${DOCKER_TAG}..."
                    sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."

                    echo "Removing old container if exists..."
                    sh """
                        if [ \$(docker ps -a -q -f name=flask-app) ]; then
                            docker rm -f flask-app
                        fi
                    """

                    echo "Running Docker container on port ${APP_PORT}..."
                    sh "docker run -d --name flask-app -p ${APP_PORT}:5000 ${DOCKER_IMAGE}:${DOCKER_TAG}"
                }
            }
        }

        stage('Wait for App to Start') {
            steps {
                echo "Waiting 10 seconds for Flask app to start..."
                sh "sleep 10"
            }
        }

        stage('OWASP ZAP Scan') {
            steps {
                echo "Run OWASP ZAP CLI scan pointing to http://<EC2_PUBLIC_IP>:${APP_PORT}"
                // Example (adjust according to your ZAP CLI command):
                sh "zap-cli quick-scan --self-contained --start-options '-config api.disablekey=true' http://18.216.252.43 :${APP_PORT}"
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
            echo "Cleaning up: stopping and removing container, cleaning workspace..."
            sh """
                docker rm -f flask-app || true
                docker rmi ${DOCKER_IMAGE}:${DOCKER_TAG} || true
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

