pipeline {
    agent { label 'mgmt' }

    stages {

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