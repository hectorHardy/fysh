resource "aws_dynamodb_table" "user_pins" {
  name           = "c22-fysh-user-pins"
  billing_mode   = "PAY_PER_REQUEST" # Scales automatically with your map traffic
  hash_key       = "user_id"         # Partition Key
  range_key      = "created_at"      # Sort Key

  attribute {
    name = "user_id"
    type = "S" # String
  }

  attribute {
    name = "created_at"
    type = "S" # String (ISO 8601 format recommended: "2026-04-20T22:00:00Z")
  }

}