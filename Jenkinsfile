pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh '''#!/bin/bash
sudo docker-compose build
sudo docker push localhost:5000/keyist-client:latest
sudo docker push localhost:5000/keyist-resource-server:latest
sudo docker push localhost:5000/keyist-authorization-server:latest'''
      }
    }

    stage('Attestation') {
      steps {
        sh '''#!/bin/bash
python -m venv tmp-py-env
source tmp-py-env/bin/activate
pip install -r in-toto/requirements.txt

cd in-toto/functionary_packer
cp -pr ../functionary_senthil/manifest/ .
in-toto-run --verbose --step-name package --use-dsse --materials manifest/client-deployment.yaml --products manifest.tar.gz --signing-key packer -- tar --exclude ".git" -zcvf manifest.tar.gz manifest
rm -rf manifest
cd ..
cp owner_secop/secop.pub owner_secop/root.layout functionary_senthil/clone.210dcc50.link functionary_senthil/update-version.210dcc50.link functionary_packer/package.be06db20.link functionary_packer/manifest.tar.gz final_product/
cd final_product
in-toto-verify --verbose --layout root.layout --verification-keys secop.pub'''
      }
    }

    stage('Deploy') {
      steps {
        sh '''#!/bin/bash
rm -rf k8s/manifest/
tar xvf in-toto/final_product/manifest.tar.gz -C k8s/
kubectl apply -f k8s/manifest/'''
      }
    }

  }
}