pipeline {

  environment {
    dockerAuthImageName = "hkvge777/web_store_auth"
    dockerBackendImageName = "hkvge777/web_store_backend"
    dockerCryptoImageName = "hkvge777/web_store_crypto"
    dockerAuthImage = ""
    dockerBackendImage = ""
    dockerCryptoImage = ""
  }

  agent any

  stages {
    stage('Build image') {
      steps{
        script {
            dockerAuthImage = docker.build(dockerAuthImageName, "-f auth/Dockerfile.auth .")
            dockerBackendImage = docker.build(dockerBackendImageName, "-f backend/Dockerfile.backend .")
            dockerCryptoImage = docker.build(dockerCryptoImageName, "-f crypto/Dockerfile.crypto .")
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
          }
        }
      }
    }

    stage('Deploying containers to Kubernetes') {
            steps {
                script {
                    def manifestDir = 'k8s'
                    def manifests = findFiles(glob: "${manifestDir}/**/*.yaml")
                    def manifestPaths = manifests.collect { it.path }
                    kubernetesDeploy(configs: manifestPaths)
                }
            }
        }

  }

}