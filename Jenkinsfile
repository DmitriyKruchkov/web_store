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

    stage('Checkout Source') {
      steps {
        git 'https://github.com/DmitriyKruchkov/web_store.git'
      }
    }

    stage('Build image') {
      steps{
        script {
          dockerAuthImage = docker.build dockerAuthImageName
          dockerBackendImage = docker.build dockerBackendImageName
          dockerCryptoImage = docker.build dockerCryptoImageName

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