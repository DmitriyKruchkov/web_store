pipeline {

  environment {
    KUBECONFIG = credentials('kubeconfig')
    dockerAuthImageName = "hkvge777/web_store_auth"
    dockerBackendImageName = "hkvge777/web_store_backend"
    dockerCryptoImageName = "hkvge777/web_store_crypto"
    dockerAlerterImageName = "hkvge777/web_store_alerter"
    dockerAuthImage = ""
    dockerBackendImage = ""
    dockerCryptoImage = ""
    dockerAlerterImage = ""
  }

  agent any

  stages {
    stage('Build image') {
      steps{
        script {
            dir('auth') {
                dockerAuthImage = docker.build(dockerAuthImageName, "-f Dockerfile.auth .")
            }
            dir('backend') {
                dockerBackendImage = docker.build(dockerBackendImageName, "-f Dockerfile.backend .")
            }
            dir('crypto') {
                dockerCryptoImage = docker.build(dockerCryptoImageName, "-f Dockerfile.crypto .")
            }
            dir('telegram_alerter') {
                dockerAlerterImage = docker.build(dockerAlerterImageName, "-f Dockerfile.alerter .")
            }
        }
      }
    }

    stage('Pushing Image') {
      environment {
               registryCredential = 'dockerhub-credentials'
           }
      steps{
        script {
          docker.withRegistry( 'https://registry.hub.docker.com', registryCredential ) {
            dockerAuthImage.push("latest")
            dockerBackendImage.push("latest")
            dockerCryptoImage.push("latest")
            dockerAlerterImage.push("latest")

          }
        }
      }
    }

    stage('Deploying containers to Kubernetes') {
            steps {
                script {
                    sh "helm upgrade --install app helm/web_store_chart \
                          --set s3_data.host=$S3_HOST \
                          --set s3_data.port=$S3_PORT \
                          --set s3_data.access_key=$S3_ACCESS_KEY \
                          --set s3_data.secret_key=$S3_SECRET_KEY \
                          --set s3_data.bucket_name=$S3_BUCKET \
                          --set telegram_bot_token=$TELEGRAM_BOT_TOKEN"
                }
            }
        }

  }

}