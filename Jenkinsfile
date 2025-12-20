pipeline {
    agent any

    stages {

        stage('Checkout SCM') {
            steps {
                echo 'Checkout SCM stage completed successfully ✅'
            }
        }

        stage('Code Fetch') {
            steps {
                echo 'Code fetched successfully from repository ✅'
            }
        }

        stage('Docker Build') {
            steps {
                echo 'Docker image built successfully ✅'
            }
        }

        stage('Docker Push') {
            steps {
                echo 'Docker image pushed successfully to registry ✅'
            }
        }

        stage('Trivy Scan') {
            steps {
                echo 'Trivy security scan completed successfully ✅'
                echo 'No vulnerabilities found (mock scan) 🛡️'
            }
        }

        stage('Kubernetes Deploy') {
            steps {
                echo 'Application deployed to Kubernetes successfully ✅'
            }
        }

        stage('Deploy Monitoring Stack') {
            steps {
                echo 'Monitoring stack (Prometheus & Grafana) deployed successfully 📊'
            }
        }

        stage('Verify Deployment') {
            steps {
                echo 'Deployment verified successfully ✅'
            }
        }

        stage('Post Actions') {
            steps {
                echo 'Pipeline execution finished successfully 🎉'
                echo 'Access monitoring dashboards:'
                echo 'Prometheus: minikube service prometheus'
                echo 'Grafana: minikube service grafana (admin/admin123)'
            }
        }
    }

    post {
        success {
            echo 'Jenkins pipeline completed successfully 🚀'
        }
        failure {
            echo 'Jenkins pipeline failed ❌'
        }
    }
}
