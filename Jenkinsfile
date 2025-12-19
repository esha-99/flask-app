pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "eshashamraiz2004/flask-app"
        DOCKER_TAG   = "${BUILD_NUMBER}"
        DOCKERHUB_CREDENTIALS = 'dockerhub-credentials' // Jenkins DockerHub credentials ID
        APP_PORT = "5000" // Flask app port
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
                    sh "docker run -d --name flask-app -p 5001:5000 ${DOCKER_IMAGE}:${DOCKER_TAG}"
                }
            }
        }

        stage('Run Docker Container') {
            steps {
                script {
                    echo "Running Docker container ${DOCKER_IMAGE}:${DOCKER_TAG}..."
                    // Stop any previous container with same name
                    sh "docker rm -f flask-app || true"
                    // Run container in detached mode
                    sh "docker run -d --name flask-app -p ${APP_PORT}:${APP_PORT} ${DOCKER_IMAGE}:${DOCKER_TAG}"
                }
            }
        }

        stage('Wait for App to Start') {
            steps {
                script {
                    echo "Waiting for Flask app to be up..."
                    // Wait a few seconds to ensure the app is ready
                    sh "sleep 10"
                }
            }
        }

        stage('OWASP ZAP Ready for Scan') {
            steps {
                echo "Your app is running at http://localhost:${APP_PORT}."
                echo "You can now scan it using OWASP ZAP CLI or container."
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
            sh "docker rm -f flask-app || true"
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
