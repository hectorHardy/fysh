data "aws_ecr_repository" "api_repo" {
    name = "c22-fysh-flask-image"
} 

resource "aws_lambda_function" "flask_api" {
  function_name = "c22-fysh-flask-api"
  role          = aws_iam_role.lambda_exec.arn
  
  # Deploying from the ECR Image
  package_type = "Image"
  image_uri    = "${data.aws_ecr_repository.api_repo.repository_url}:latest"

  timeout     = 30
  memory_size = 512

  environment {
    variables = {
      CLIENT_ID = aws_cognito_user_pool_client.client.id
    }
  }
}

# --- 2. IAM Role & Policies ---
resource "aws_iam_role" "lambda_exec" {
  name = "c22-fysh-flask-lambda-exec-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

# Policy for Logs, DynamoDB, and Cognito access
resource "aws_iam_role_policy" "lambda_permissions" {
  name = "c22-fysh-flask-lambda-permissions"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        # Permission for CloudWatch Logs
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
        Effect   = "Allow"
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        # Permission for your DynamoDB user history table
        Action   = ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:Query"]
        Effect   = "Allow"
        Resource = "*" # Replace with your DynamoDB Table ARN for tighter security
      },
      {
        # Permission for Cognito Auth actions
        Action   = ["cognito-idp:SignUp", "cognito-idp:ConfirmSignUp", "cognito-idp:InitiateAuth", "cognito-idp:GetUser"]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

# --- 3. API Gateway (HTTP API) ---
resource "aws_apigatewayv2_api" "http_api" {
  name          = "c22-fysh-flask-serverless-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true
}

# Integration between API Gateway and Lambda
resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.flask_api.invoke_arn
  payload_format_version = "2.0"
}

# Greedy Proxy Route: Forwards everything to Flask
resource "aws_apigatewayv2_route" "any_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

# Permission for API Gateway to invoke Lambda
resource "aws_lambda_permission" "api_gw_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.flask_api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

# --- Outputs ---
output "base_url" {
  value = aws_apigatewayv2_api.http_api.api_endpoint
}