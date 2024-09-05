pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh '''sudo docker-compose build
sudo docker push localhost:5000/keyist-client:latest
sudo docker push localhost:5000/keyist-resource-server:latest
sudo docker push localhost:5000/keyist-authorization-server:latest'''
      }
    }

    stage('Deploy') {
      steps {
        sh '''kubectl apply -f k8s/manifest/'''
      }
    }

  }
}
