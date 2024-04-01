pipeline {
    // agent any
    agent {
        docker {
            image 'python:3.10-alpine'
        }
    }

    stages {
        stage('Build') {
            steps {
                // script {
                //     docker.image('python:3.9-alpine').inside {
                //         // Sklonuj repozytorium Git
                //         git branch: 'main', url: 'git@github.com:wilduk/Projekt.git'

                //         // Zainstaluj zależności
                //         sh 'pip install -r requirements.txt'

                //         // Wykonaj inne operacje budowania
                //         sh 'python setup.py build'
                //     }
                // }
                // Get some code from a GitHub repository
                git branch: 'main', url: 'git@github.com:wilduk/Projekt.git'
                // sh "pip install django"

                sh "echo HELLO"
            }

            post {
                always {
                    sh "echo YES"
                    script {
                        def message = (currentBuild.currentResult == 'SUCCESS') ? '💪 Success' : '💥 Build failed'
                        echo message
                        // discordSend description: "Jenkins Pipeline Build", footer: message, link: env.BUILD_URL, result: currentBuild.currentResult, title: JOB_NAME, webhookURL: "https://discord.com/api/webhooks/1224373332481146952/Dl3SgWjT00TibMkbVCBvRPPD_loK06cYngCe30-Xeotw-5JioCWGebRLqOUL9o46O0-K"
                    }
                }
            }
        }
    }
}
