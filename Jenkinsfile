#!groovy
properties([
    pipelineTriggers([[$class:"GitHubPushTrigger"]])
])
pipeline {
  agent { label 'docker-slave' }
  stages{
    stage('Get Code') {
      steps {
          deleteDir()
          checkout ([
              $class: 'GitSCM',
              branches: scm.branches,
              doGenerateSubmoduleConfigurations: scm.doGenerateSubmoduleConfigurations,
              extensions: [[$class: 'CloneOption', noTags: false, shallow: false, depth: 0, reference: '']],
              userRemoteConfigs: scm.userRemoteConfigs,
           ])
           script {
               tag=sh(returnStdout: true, script: "git tag -l --points-at HEAD").trim()
               env.tag = tag
             }
      }
    }
    stage('GetOpsScripts') {
      steps {
        slackSend (color: '#ddaa00', message: ":construction_worker: kf-api-release-coordinator GETTING SCRIPTS:")
        sh '''
        git clone git@github.com:kids-first/kf-api-release-coordinator-config.git
        '''
      }
    }
    stage('Test') {
     steps {
       slackSend (color: '#ddaa00', message: ":construction_worker: kf-api-release-coordinator TESTING STARTED: (${env.BUILD_URL})")
       sh '''
       kf-api-release-coordinator-config/aws-ecs-service-type-1/ci-scripts/test_stage/test.sh
       '''
       slackSend (color: '#41aa58', message: ":white_check_mark: kf-api-release-coordinator TESTING COMPLETED: (${env.BUILD_URL})")
     }
     post {
       failure {
         slackSend (color: '#ff0000', message: ":frowning: kf-api-release-coordinator Test Failed: Branch '${env.BRANCH_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})")
       }
     }
    }
    stage('Build') {
      steps {
        sh '''
        kf-api-release-coordinator-config/aws-ecs-service-type-1/ci-scripts/build_stage/build.sh
        '''
      }
    }
    stage('Publish') {
      steps {
        sh '''
        kf-api-release-coordinator-config/aws-ecs-service-type-1/ci-scripts/publish_stage/publish.sh
        '''
        slackSend (color: '#41aa58', message: ":arrow_up: kf-api-release-coordinator PUSHED IMAGE: (${env.BUILD_URL})")
      }
      post {
        failure {
          slackSend (color: '#ff0000', message: ":frowning: kf-api-release-coordinator Publish Failed: Branch '${env.BRANCH_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})")
        }
      }
    }
    stage('Deploy Dev') {
      when {
        expression {
          return env.BRANCH_NAME != 'master';
        }
      }
      steps {
        slackSend (color: '#005e99', message: ":deploying_dev: DEPLOYING TO DEVELOPMENT: (${env.BUILD_URL})")
        sh '''
        kf-api-release-coordinator-config/aws-ecs-service-type-1/ci-scripts/deploy_stage/deploy.sh dev
        '''
        slackSend (color: '#41aa58', message: ":white_check_mark: kf-api-release-coordinator DEPLOYED TO DEVELOPMENT: (${env.BUILD_URL})")
      }
      post {
        failure {
          slackSend (color: '#ff0000', message: ":frowning: kf-api-release-coordinator Test Failed: Branch '${env.BRANCH_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})")
        }
      }
    }
    stage('Retag with pre-release'){
      when {
        expression {
            return env.BRANCH_NAME == 'master';
        }
        expression {
          return tag != '';
        }
      }
      steps {
        slackSend (color: '#005e99', message: ":deploying_qa: Retagging image with 'pre-release'")
        sh '''
          MANIFEST=$(aws ecr batch-get-image --region us-east-1 --repository-name kf-api-release-coordinator --image-ids imageTag=latest --query images[].imageManifest --output text)
          aws ecr put-image --region us-east-1 --repository-name kf-api-release-coordinator --image-tag "prerelease-$tag" --image-manifest "$MANIFEST"
        '''
      }
    }
    stage('Deploy QA') {
      when {
       expression {
           return env.BRANCH_NAME == 'master';
       }
     }
     steps {
       slackSend (color: '#005e99', message: ":deploying_qa: kf-api-release-coordinator DEPLOYING TO QA: (${env.BUILD_URL})")
       sh '''
       kf-api-release-coordinator-config/aws-ecs-service-type-1/ci-scripts/deploy_stage/deploy.sh qa
       '''
       slackSend (color: '#41aa58', message: ":white_check_mark: kf-api-release-coordinator DEPLOYED TO QA: (${env.BUILD_URL})")
     }
    }
    stage("Promotion kf-api-release-coordinator to PRD") {
      when {
             expression {
               return env.BRANCH_NAME == 'master';
             }
             expression {
               return tag != '';
             }
           }
      steps {
             script {
                     env.DEPLOY_TO_PRD = input message: 'User input required',
                                     submitter: 'lubneuskia,heatha',
                                     parameters: [choice(name: 'kf-api-release-coordinator: Deploy to PRD Environment', choices: 'no\nyes', description: 'Choose "yes" if you want to deploy the PRD server')]
             }
     }
    }
    stage('Retag with release'){
      when {
        environment name: 'DEPLOY_TO_PRD', value: 'yes'
        expression {
            return env.BRANCH_NAME == 'master';
        }
        expression {
          return tag != '';
        }
      }
      steps {
        slackSend (color: '#005e99', message: ":deploying_qa: kf-api-release-coordinator Retagging image with 'release'")
        sh '''
          MANIFEST=$(aws ecr batch-get-image --region us-east-1 --repository-name kf-api-release-coordinator --image-ids imageTag="prerelease-$tag" --query images[].imageManifest --output text)
          aws ecr put-image --region us-east-1 --repository-name kf-api-release-coordinator --image-tag "$tag" --image-manifest "$MANIFEST"
        '''
      }
    }
    stage('Deploy PRD') {
      when {
       environment name: 'DEPLOY_TO_PRD', value: 'yes'
       expression {
           return env.BRANCH_NAME == 'master';
       }
       expression {
         return tag != '';
       }
     }
     steps {
       slackSend (color: '#005e99', message: ":deploying_prd: kf-api-release-coordinator DEPLOYING TO PRD: (${env.BUILD_URL})")
       sh '''
       kf-api-release-coordinator-config/aws-ecs-service-type-1/ci-scripts/deploy_stage/deploy.sh prd
       '''
       slackSend (color: '#41aa58', message: ":white_check_mark: kf-api-release-coordinator DEPLOYED TO PRD: (${env.BUILD_URL})")
     }
    }
    stage("Rollback to previous version of the application with DB Rollback") {
      when {
             expression {
               return env.BRANCH_NAME == 'master';
             }
             expression {
               return tag != '';
             }
           }
      steps {
             script {
                     env.ROLLBACK_PRD = input message: 'User input required',
                                     submitter: 'lubneuskia,heatha',
                                     parameters: [choice(name: 'kf-api-release-coordinator: Rollback PRD to Previous Version?', choices: 'no\nyes', description: 'Choose "yes" if you want to rollback the PRD deployment to previous stable release')]
             }
     }
    }
    stage('Rollback PRD') {
      when {
       environment name: 'ROLLBACK_PRD', value: 'yes'
       expression {
           return env.BRANCH_NAME == 'master';
       }
       expression {
         return tag != '';
       }
     }
     steps {
       slackSend (color: '#005e99', message: ":deploying_prd: kf-api-release-coordinator DEPLOYING TO PRD: (${env.BUILD_URL})")
       sh '''
       kf-api-release-coordinator-config/aws-ecs-service-type-1/ci-scripts/rollback/rollback.sh
       '''
       slackSend (color: '#41aa58', message: ":white_check_mark: kf-api-release-coordinator DEPLOYED TO PRD: (${env.BUILD_URL})")
     }
    }
  }
}
