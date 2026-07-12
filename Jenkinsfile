pipeline {
    agent any

    stages {
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t attendance-app .'
            }
        }

        stage('Stop Existing Container') {
            steps {
                sh 'docker stop attendance-container || true'
                sh 'docker rm attendance-container || true'
            }
        }

        stage('Run Container') {
            steps {
                sh 'docker run -d --name attendance-container -p 8000:8000 attendance-app'
            }
        }
    }
}