@Library(value="kids-first/aws-infra-jenkins-shared-libraries@master", changelog=false) _
ecs_service_type_1_standard {
    projectName = "kf-api-release-coordinator"
    environments = "dev,qa,prd"
    docker_image_type = "alpine"
    entrypoint_command = "/app/bin/entrypoint.sh" 
    deploy_scripts_version = "master"
    quick_deploy = "false"
    internal_app = "false"
    container_port = "80"
    vcpu_container             = "2048"
    memory_container           = "4096"
    vcpu_task                  = "2048"
    memory_task                = "4096"
    health_check_path = "/oauth/token/public_key"
    dependencies = "ecr"
    friendly_dns_name = "release-coordinator"
}
