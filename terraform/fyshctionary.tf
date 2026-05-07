resource "aws_dynamodb_table" "fysh_dictionary" {
    name          = "fyshctionary"
    billing_mode  = "PAY_PER_REQUEST"
    hash_key      = "fish_id"

    attribute {
        name = "fish_id"
        type = "S"
    }

    attribute {
        name = "water_type"
        type = "S"
    }

    global_secondary_index {
        name            = "WaterTypeIndex"
        hash_key        = "water_type"
        range_key       = "fish_id"
        projection_type = "ALL"
  }
}
