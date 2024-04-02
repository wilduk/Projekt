pipeline {
    agent any

    environment {
        PROJECT_VERSION = new Date().format("yyMMdd.HHmm", TimeZone.getTimeZone('CET'))
        GITEA_URL = 'https://gitea.pack.force.ovh/api/v1/'
        GITEA_CREDENTIALS_ID = 'ce728f40-5dd4-4fa6-837c-bad3723693a6'
        PORTAINER_API_URL = 'https://portainer.pack.force.ovh/api/'
        PORTAINER_STACK_ID = '5'
        PIP_CACHE_DIR = '/var/jenkins_home/_cache/pip'
        PYTHONUSERBASE = '/var/jenkins_home/_local'
        DISCORD_WEBHOOK_URL = credentials('DISCORD_WEBHOOK_URL')
    }

    stages {
        stage('Build image') {
            steps {
                script {
                    def version = env.PROJECT_VERSION
                    def image = "gitea.pack.force.ovh/lapserdaki/projekt-kanban:$version"
                    env.IMAGE_NAME = image
                    echo "Version: $version"
                    echo "Image: $image"

                    git branch: 'main', url: 'git@github.com:wilduk/Projekt.git'
                    docker.build(env.IMAGE_NAME, "-f Dockerfile .")
                }
            }

            post {
                unsuccessful {
                    script {
                        def icon = '💥'
                        def message = "$icon Image build failed"
                        echo message
                        discordSend description: "Jenkins Pipeline: Build image", footer: message, link: env.BUILD_URL, result: currentBuild.currentResult, title: JOB_NAME, webhookURL: env.DISCORD_WEBHOOK_URL
                    }
                }
            }
        }
        stage('Push Docker Image') {
            steps {
                script {
                    // Wysyłanie obrazu Docker na prywatne repozytorium Gitea
                    echo 'PUSH'
                    docker.withRegistry(env.GITEA_URL, env.GITEA_CREDENTIALS_ID) {
                        docker.image(env.IMAGE_NAME).push()
                    }
                }
            }
            post {
                always {
                    script {
                        def icon = (currentBuild.currentResult == "SUCCESS") ? '💪' : '💥'
                        def message = (currentBuild.currentResult == "SUCCESS") ? "$icon Image built and pushed to gitea registry, version: ${env.PROJECT_VERSION}. Deploying to prod..." : "$icon Image push failed"
                        echo message
                        discordSend description: "Jenkins Pipeline: Build", footer: message, link: env.BUILD_URL, result: currentBuild.currentResult, title: JOB_NAME, webhookURL: env.DISCORD_WEBHOOK_URL
                    }
                }
            }
        }
        stage('Redeploy Stack in Portainer') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'PORTAINER_TOKEN', variable: 'PORTAINER_TOKEN')]) {
                        def apiToken = env.PORTAINER_API_TOKEN
                        def apiKeyHeader = "-H 'X-API-Key:$apiToken'"

                        docker.image('python:3.10-alpine').inside {
                            git branch: 'deploy', url: 'git@github.com:wilduk/Projekt.git'
                            sh 'pip install requests==2.31.0'
                            def result = sh script: "python deploy.py ${env.PORTAINER_API_URL} ${PORTAINER_TOKEN} ${env.PORTAINER_STACK_ID} ${env.PROJECT_VERSION}", returnStdout: true
                            echo result
                        }
                    }
                }
            }
            post {
                always {
                    script {
                        def icon = (currentBuild.currentResult == "SUCCESS") ? '🚀' : '💥'
                        def message = (currentBuild.currentResult == "SUCCESS") ? "$icon Project successfully deployed to prod, version: ${env.PROJECT_VERSION}" : "$icon Deployment failed"
                        echo message
                        discordSend description: "Jenkins Pipeline: Deploy", footer: message, link: env.BUILD_URL, result: currentBuild.currentResult, title: JOB_NAME, webhookURL: env.DISCORD_WEBHOOK_URL
                    }
                }
            }
        }
    }
}
