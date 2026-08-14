pipeline {
    agent { label 'mgmt' }

    stages {
           stage('SonarQube Analysis') {
            when {
                anyOf {
                    branch 'develop'
                    branch 'main'
                }
            }
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'
                    withCredentials([string(credentialsId: 'NOPPAKAO_SONAR_TOKEN', variable: 'SONAR_TOKEN')]) {
                        withSonarQubeEnv() {
                            sh "${scannerHome}/bin/sonar-scanner -Dsonar.token=\$SONAR_TOKEN"
                        }
                    }
                }
            }
        }
        stage('Deploy to Staging') {
            when {
                branch 'develop'
            }
            steps {
                withCredentials([
                    sshUserPrivateKey(credentialsId: 'r202-staging-ssh', keyFileVariable: 'SSH_KEY', usernameVariable: 'SSH_USER'),
                    string(credentialsId: 'r202-staging-host', variable: 'SSH_HOST'),
                    string(credentialsId: 'r202-staging-port', variable: 'SSH_PORT')
                ]) {
                    sh '''
                        echo "Starting deployment to Staging server..."
                        
                        ssh -i $SSH_KEY -p $SSH_PORT -o StrictHostKeyChecking=no $SSH_USER@$SSH_HOST "
                            
                            echo '==> Deploying noppakao Staging...'
                            cd /home/projects/noppakao
                            git -C /home/projects/noppakao fetch origin develop
                            git -C /home/projects/noppakao checkout develop
                            git -C /home/projects/noppakao reset --hard origin/develop
                            git -C /home/projects/noppakao pull
                            docker compose -f docker-compose.staging.yml up -d --build --force-recreate

                        "
                        echo "Deployment process finished successfully!"
                    '''
                }
            }
        }

        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                withCredentials([
                    sshUserPrivateKey(credentialsId: 'noppakao-prod-ssh', keyFileVariable: 'SSH_KEY', usernameVariable: 'SSH_USER'),
                    string(credentialsId: 'noppakao-prod-host', variable: 'SSH_HOST'),
                    string(credentialsId: 'noppakao-prod-port', variable: 'SSH_PORT')
                ]) {
                    sh '''
                        echo "Starting deployment to Production server..."
                        
                        ssh -i $SSH_KEY -p $SSH_PORT -o StrictHostKeyChecking=no $SSH_USER@$SSH_HOST "
                            echo '==> Deploying noppakao...'
                            cd /home/projects/noppakao
                            sudo git -C /home/projects/noppakao fetch origin main
                            sudo git -C /home/projects/noppakao checkout main
                            sudo git -C /home/projects/noppakao reset --hard origin/main
                            sudo git -C /home/projects/noppakao pull origin main
                            sudo docker compose -f docker-compose.yml up -d --build --force-recreate
                        "
                        echo "Deployment process finished successfully!"
                    '''
                }
            }
        }
    }
}