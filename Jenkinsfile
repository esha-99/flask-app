pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'eshashamraiz2004/flask-app'
        DOCKER_TAG = "${BUILD_NUMBER}"
        DOCKER_CREDENTIALS = 'dockerhub-credentials'
        GITHUB_CREDENTIALS = 'github-credentials'
        SONARQUBE_ENV = 'SonarQube'
        KUBECONFIG = credentials('kubeconfig')
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
                script {
                    def scannerHome = tool 'SonarQubeScanner'
                    withSonarQubeEnv("${SONARQUBE_ENV}") {
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectKey=flask-app \
                            -Dsonar.sources=. \
                            -Dsonar.host.url=http://localhost:9000 \
                            -Dsonar.python.coverage.reportPaths=coverage.xml
                        """
                    }
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
                    pip3 install safety
                    safety check --json || true
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                    docker.build("${DOCKER_IMAGE}:latest")
                }
            }
        }
        
        stage('Container Scan - Trivy') {
            steps {
                sh """
                    trivy image --severity HIGH,CRITICAL \
                    --format json \
                    --output trivy-report.json \
                    ${DOCKER_IMAGE}:${DOCKER_TAG}
                    
                    trivy image --severity HIGH,CRITICAL \
                    ${DOCKER_IMAGE}:${DOCKER_TAG}
                """
            }
        }
        
        stage('Push to DockerHub') {
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', "${DOCKER_CREDENTIALS}") {
                        dockerImage.push("${DOCKER_TAG}")
                        dockerImage.push("latest")
                    }
                }
            }
        }
        
        stage('Update Kubernetes Manifests') {
            steps {
                sh """
                    sed -i 's|image:.*|image: ${DOCKER_IMAGE}:${DOCKER_TAG}|g' k8s/deployment.yaml
                """
            }
        }
        
        stage('Deploy to Kubernetes') {
            steps {
                script {
                    sh """
                        export KUBECONFIG=${KUBECONFIG}
                        kubectl apply -f k8s/namespace.yaml
                        kubectl apply -f k8s/deployment.yaml
                        kubectl apply -f k8s/service.yaml
                        kubectl apply -f k8s/networkpolicy.yaml
                        kubectl rollout status deployment/flask-app -n flask-app
                    """
                }
            }
        }
        
        stage('DAST - OWASP ZAP Scan') {
            steps {
                script {
                    sh """
                        # Get service URL
                        SERVICE_URL=\$(kubectl get svc flask-app-service -n flask-app -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
                        
                        # Run ZAP baseline scan
                        docker run --rm \
                        -v \$(pwd):/zap/wrk/:rw \
                        -t ghcr.io/zaproxy/zaproxy:stable zap-baseline.py \
                        -t http://\${SERVICE_URL} \
                        -r zap-report.html \
                        -J zap-report.json || true
                    """
                }
            }
        }
        
        stage('Kubernetes Security Scan') {
            steps {
                sh """
                    # Scan Kubernetes manifests
                    trivy config k8s/ --format json --output k8s-scan-report.json
                    trivy config k8s/
                """
            }
        }
        
        stage('Generate Reports') {
            steps {
                sh '''
                    echo "Security Scan Summary" > security-report.txt
                    echo "=====================" >> security-report.txt
                    echo "" >> security-report.txt
                    echo "Trivy Container Scan Results:" >> security-report.txt
                    cat trivy-report.json >> security-report.txt
                    echo "" >> security-report.txt
                    echo "Kubernetes Security Scan:" >> security-report.txt
                    cat k8s-scan-report.json >> security-report.txt
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
            echo 'Pipeline executed successfully!'
            // Add Slack/Email notification here
        }
        failure {
            echo 'Pipeline failed!'
            // Add Slack/Email notification here
        }
    }
}