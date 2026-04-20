resource "aws_cognito_user_pool" "main" {
  name = "c22-fysh-user-pool"

  # Allow users to sign themselves up
  admin_create_user_config {
    allow_admin_create_user_only = false
  }

  # Configure which attributes are required/verified
  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]

  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }
}

resource "aws_cognito_user_pool_client" "client" {
  name         = "c22-fysh-app-client"
  user_pool_id = aws_cognito_user_pool.main.id

  # Explicitly allow the Auth Flows you'll use in Boto3
  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH", # Standard login
    "ALLOW_REFRESH_TOKEN_AUTH", # For staying logged in
    "ALLOW_USER_SRP_AUTH"       # Secure Remote Password (recommended)
  ]

  # For backend/server-side scripts, you might want a secret.
  # For frontend apps, leave this false.
  generate_secret = false
}

resource "aws_dynamodb_table" "user_data" {
  name           = "c22-fysh-user-data"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "user_id"

  attribute {
    name = "user_id"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }
}

output "user_pool_id" { value = aws_cognito_user_pool.main.id }
output "client_id"    { value = aws_cognito_user_pool_client.client.id }