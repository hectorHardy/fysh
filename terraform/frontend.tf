# --- 1. S3 BUCKET SETUP ---

resource "aws_s3_bucket" "website_bucket" {
  bucket = "c22-fysh-website-bucket" # Change this to a unique name!
}

# Block all public access to the bucket (essential for security)
resource "aws_s3_bucket_public_access_block" "block_public" {
  bucket = aws_s3_bucket.website_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# --- 2. CLOUDFRONT ORIGIN ACCESS CONTROL (OAC) ---

resource "aws_cloudfront_origin_access_control" "default" {
  name                              = "c22-fysh-s3-oac-config"
  description                       = "Allows CloudFront to reach the private S3 bucket"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# --- 3. CLOUDFRONT DISTRIBUTION ---

resource "aws_cloudfront_distribution" "s3_distribution" {
  origin {
    domain_name              = aws_s3_bucket.website_bucket.bucket_regional_domain_name
    origin_id                = "S3Origin"
    origin_access_control_id = aws_cloudfront_origin_access_control.default.id
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  # Standard Cache Behavior
  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3Origin"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = {
    Environment = "Production"
  }
}

# --- 4. BUCKET POLICY (THE "BRIDGE") ---

resource "aws_s3_bucket_policy" "cloudfront_oac_policy" {
  bucket = aws_s3_bucket.website_bucket.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = "s3:GetObject"
        Effect   = "Allow"
        Resource = "${aws_s3_bucket.website_bucket.arn}/*"
        Principal = {
          Service = "cloudfront.amazonaws.com"
        }
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = aws_cloudfront_distribution.s3_distribution.arn
          }
        }
      }
    ]
  })
}

# --- 5. OUTPUTS ---

output "cloudfront_url" {
  value       = aws_cloudfront_distribution.s3_distribution.domain_name
  description = "The URL of your website"
}

output "s3_bucket_name" {
  value = aws_s3_bucket.website_bucket.id
}