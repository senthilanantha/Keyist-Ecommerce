pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        cleanWs(deleteDirs: true, disableDeferredWipeout: true, notFailBuild: true)
        checkout scm
        sh '''#!/bin/bash
sudo docker-compose build
sudo docker push localhost:5000/keyist-client:latest
sudo docker push localhost:5000/keyist-resource-server:latest
sudo docker push localhost:5000/keyist-authorization-server:latest'''
        sh '''#!/bin/bash
cd client
npm install'''
      }
    }

    stage('Attestation') {
      steps {
        sh '''#!/bin/bash
python -m venv tmp-py-env
source tmp-py-env/bin/activate
pip install -r in-toto/requirements.txt

cd in-toto/functionary_packer
rm -f manifest
rm -rf *.link
cp -pr ../functionary_senthil/manifest/ .
in-toto-run --verbose --step-name package --use-dsse --materials manifest/client-deployment.yaml --products manifest.tar.gz --signing-key packer -- tar --exclude ".git" -zcvf manifest.tar.gz manifest
rm -rf manifest
cd ..
rm -rf final_product/*
cp owner_secop/secop.pub owner_secop/root.layout functionary_senthil/clone.210dcc50.link functionary_senthil/update-version.210dcc50.link functionary_packer/package.be06db20.link functionary_packer/manifest.tar.gz final_product/
cd final_product
in-toto-verify --verbose --layout root.layout --verification-keys secop.pub'''
      }
    }

    stage('SCA') {
      steps {
        dependencyCheck(odcInstallation: 'DP-check', additionalArguments: '--format HTML')
      }
    }

    stage('SAST-Auth') {
      parallel {
        stage('SAST-Auth-Java') {
          steps {
            sh '''#!/bin/bash
cd authorization_server
mvn clean verify sonar:sonar \\
  -Dsonar.projectKey=auth_server \\
  -Dsonar.projectName=\'auth_server\' \\
  -Dsonar.host.url=http://localhost:9000 \\
  -Dsonar.token=sqp_b22d4407ea4315954f2f0f2df84ae46f09dd2eb4'''
          }
        }

        stage('SAST-Resource-Java') {
          steps {
            sh '''#!/bin/bash
cd resource_server
mvn clean verify sonar:sonar \\
  -Dsonar.projectKey=resource_server \\
  -Dsonar.projectName=\'resource_server\' \\
  -Dsonar.host.url=http://localhost:9000 \\
  -Dsonar.token=sqp_b22d4407ea4315954f2f0f2df84ae46f09dd2eb4'''
          }
        }

        stage('SAST-Client-Angular') {
          steps {
            sh '''#!/bin/bash
cd client
npm run sonar -- -Dsonar.token=sqp_b22d4407ea4315954f2f0f2df84ae46f09dd2eb4'''
          }
        }

      }
    }

    stage('Deploy') {
      steps {
        sh '''#!/bin/bash
kubectl apply -f in-toto/final_product/manifest/'''
      }
    }

  }
  options {
    skipDefaultCheckout(true)
  }
}