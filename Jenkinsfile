pipeline {
    agent any

    environment {
        DOCKER_IMAGE        = 'eshashamraiz2004/flask-app'
        DOCKER_TAG          = "${BUILD_NUMBER}"
        DOCKER_CREDENTIALS  = 'dockerhub-credentials'
        SONARQUBE_ENV       = 'SonarQube'
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/esha-99/flask-app.git'
            }
        }

        stage('SAST - SonarQube Analysis') {
            steps {
                withSonarQubeEnv("${SONARQUBE_ENV}") {
                    sh '''
                        sonar-scanner \
                        -Dsonar.projectKey=esha-flask-app \
                        -Dsonar.sources=. \
                        -Dsonar.host.url=http://localhost:9000
                    '''
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Dependency Check') {
            steps {
                sh '''
                    pip3 install --no-cache-dir safety
                    safety check || true
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                    dockerImage.tag('latest')
                }
            }
        }

        stage('Container Scan - Trivy') {
            steps {
                sh '''
                    trivy image --severity HIGH,CRITICAL \
                    ${DOCKER_IMAGE}:${DOCKER_TAG} || true
                '''
            }
        }

        stage('Push to DockerHub') {
            steps {
                script {
                    docker.withRegistry(
                        'https://registry.hub.docker.com',
                        DOCKER_CREDENTIALS
                    ) {
                        dockerImage.push("${DOCKER_TAG}")
                        dockerImage.push("latest")
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                    kubectl apply -f k8s/namespace.yaml
                    kubectl apply -f k8s/deployment.yaml
                    kubectl apply -f k8s/service.yaml
                    kubectl rollout status deployment/flask-app -n flask-app
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: '*.json, *.html, *.txt', allowEmptyArchive: true
            cleanWs()
        }
        success {
            echo '✅ Pipeline executed successfully!'
        }
        failure {
            echo '❌ Pipeline failed!'
        }
    }
}
