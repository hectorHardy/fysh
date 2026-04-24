# Flask API for AWS Deployment

This folder contains the code and resources for deploying a Flask-based API on AWS. The API provides user authentication, pin storage, and other backend functionalities. Below is a detailed guide on the structure, functionality, and deployment process.

## Folder Structure

- **authentication.py**: Handles user authentication using AWS Cognito. Includes functions for signing up, confirming sign-ups, logging in, and deleting users.
- **backend_api.py**: The main Flask application that defines API endpoints for user authentication and other backend operations.
- **pin_storage.py**: Manages user pins in DynamoDB, allowing users to add, retrieve, and delete pins.
- **dockerfile**: Defines the Docker image for the Flask API, including dependencies and the command to run the application.
- **push_api_image.sh**: A shell script to build and push the Docker image to AWS Elastic Container Registry (ECR).
- **requirements.txt**: Lists the Python dependencies required for the API.

## Key Functionalities

### User Authentication
- **Sign Up**: Users can sign up with their email and password. A confirmation code is sent to their email for verification.
- **Log In**: Authenticated users receive an access token to interact with protected endpoints.
- **Delete Account**: Users can delete their account and associated data.

### Pin Storage
- **Add Pin**: Users can add pins with latitude, longitude, and optional features.
- **Delete Pin**: Users can delete pins based on their creation timestamp.

## Deployment Guide

### Prerequisites
1. **AWS Account**: Ensure you have an AWS account with permissions to use Cognito, DynamoDB, and ECR.
2. **Docker**: Install Docker on your local machine.
3. **AWS CLI**: Install and configure the AWS CLI with your credentials.

### Steps to Deploy

1. **Build the Docker Image**:
   ```bash
   ./push_api_image.sh
   ```
   This script will:
   - Log in to AWS ECR.
   - Build the Docker image.
   - Push the image to your ECR repository.

2. **Terraform**
    - navigate to the terraform file and run 
    ```
    terraform init
    terraform apply
    ```

### Testing the API

- Use tools like Postman or cURL to test the API endpoints.
- Example:
  ```bash
  curl -X POST -H "Content-Type: application/json" \
       -d '{"email": "test@example.com", "password": "password123"}' \
       http://<your-api-endpoint>/signup
  ```

## Notes

- Ensure proper IAM permissions for AWS resources.
- Monitor the API using AWS CloudWatch for logs and metrics.
- Update the `requirements.txt` file if new dependencies are added.