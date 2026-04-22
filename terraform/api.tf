data "aws_ecr_repository" "api_repo" {
    name = "c22-fysh-flask-image"
} 

# Trust Policy (Allows ECS tasks to assume this role)
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "c22-fysh-flask-api-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

# Attach the standard AWS managed policy for ECR and Logging
resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task_role" {
  name = "c22-fysh-api-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_policy" "flask_api_permissions" {
  name        = "c22-fysh-flask-api-access-policy"
  description = "Permissions for Cognito and DynamoDB"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # DynamoDB Permissions
      {
        Effect   = "Allow"
        Action   = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query"
        ]
        Resource = "arn:aws:dynamodb:eu-west-2:*:table/c22-fysh-user-data"
      },
      # Cognito Permissions
      {
        Effect   = "Allow"
        Action   = [
          "cognito-idp:SignUp",
          "cognito-idp:ConfirmSignUp",
          "cognito-idp:InitiateAuth",
          "cognito-idp:GetUser",
          "cognito-idp:DeleteUser"
        ]
        Resource = "*" # Or specify your User Pool ARN for tighter security
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "task_permissions_attachment" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.flask_api_permissions.arn
}

# Create a CloudWatch Log Group for ECS task logs
resource "aws_cloudwatch_log_group" "ecs_task_logs" {
  name              = "/ecs/c22-fysh-api"
  retention_in_days = 7
}

resource "aws_ecs_task_definition" "api" {
  family                   = "c22-fysh-api-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
        name      = "api-container"
        image     = "${data.aws_ecr_repository.api_repo.repository_url}:latest"
        essential = true
        portMappings = [{
            containerPort = 5000
            hostPort      = 5000
        }]
        logConfiguration = {
          logDriver = "awslogs"
          options = {
            awslogs-group         = aws_cloudwatch_log_group.ecs_task_logs.name
            awslogs-region        = var.aws_region
            awslogs-stream-prefix = "ecs"
          }
        }
    }
  ])
}

resource "aws_ecs_cluster" "api_cluster" {
    name = "c22-fysh-api-cluster"
}

resource "aws_security_group" "ecs_tasks" {
    name        = "c22-fysh-ecs-tasks-sg"
    description = "Allow inbound traffic to ECS tasks"
    vpc_id      = var.vpc_id

    ingress {
        from_port   = 5000
        to_port     = 5000
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
}


resource "aws_ecs_service" "api_service" {
  name            = "c22-fysh-api-service"
  cluster         = aws_ecs_cluster.api_cluster.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.public_subnets
    security_groups = [aws_security_group.ecs_tasks.id]

    assign_public_ip = true
  }
}