pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "eshashamraiz2004/flask-app"
        DOCKER_TAG   = "${BUILD_NUMBER}"
        DOCKERHUB_CREDENTIALS = 'dockerhub-credentials' // Jenkins DockerHub credentials ID
        SONARQUBE_SERVER = 'SonarQube' // Jenkins SonarQube server ID (set in Jenkins configuration)
        SONAR_TOKEN = credentials('sonar-token') // Add your SonarQube token as Jenkins credential
    }

    stages {
        stage('Checkout SCM') {
            steps {
                echo "Checking out code from Git..."
                checkout scm
            }
        }

        stage('SonarQube Scan') {
            steps {
                script {
                    echo "Running SonarQube scan..."
                    sh """
                        sonar-scanner \
                        -Dsonar.projectKey=flask-app \
                        -Dsonar.sources=. \
                        -Dsonar.host.url=http://18.216.252.43:9000 \
                        -Dsonar.login=${SONAR_TOKEN}
                    """
                }
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

        stage('Container Scan - Trivy') {
            steps {
                script {
                    echo "Scanning Docker image with Trivy..."
                    sh "trivy image --severity HIGH,CRITICAL ${DOCKER_IMAGE}:${DOCKER_TAG}"
                }
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

        stage('Deploy to Kubernetes') {
            when {
                expression { false } // Skipped for now
            }
            steps {
                echo "Deploy to Kubernetes logic here..."
            }
        }
    }

    post {
        always {
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
