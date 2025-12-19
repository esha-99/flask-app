pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "eshashamraiz2004/flask-app"
        DOCKER_TAG   = "${BUILD_NUMBER}"
        DOCKERHUB_CREDENTIALS = 'dockerhub-credentials' // Jenkins DockerHub credentials ID
        KUBE_CONFIG_CREDENTIALS = 'kubeconfig-credentials' // Add your kubeconfig as Jenkins secret file
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
            steps {
                script {
                    echo "Deploying to Kubernetes..."
                    // Copy kubeconfig to agent
                    withCredentials([file(credentialsId: "${KUBE_CONFIG_CREDENTIALS}", variable: 'KUBECONFIG_FILE')]) {
                        sh """
                            export KUBECONFIG=$KUBECONFIG_FILE
                            kubectl set image deployment/flask-app flask-app=${DOCKER_IMAGE}:${DOCKER_TAG} --record
                            kubectl rollout status deployment/flask-app
                        """
                    }
                }
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
