@Library(value="kids-first/aws-infra-jenkins-shared-libraries@feature/skip-wrapper-build", changelog=false) _
ecs_service_type_1_standard {
    ecs_service_type_1_version = "feature/skip-wrapper-build"
    deploy_scripts_version = "feature/skip-wrapper-build"
    projectName = "kf-api-release-coordinator"
    environments = "dev,qa,prd"
    docker_image_type = "alpine"
    entrypoint_command = "/app/bin/entrypoint.sh" 
    quick_deploy = "true"
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
