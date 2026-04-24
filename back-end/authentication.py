'''
File for authenticating a user

To add a new user:
1. Call sign_up_user to create a new user in Cognito. This will send a confirmation code to the user's email.
2. Call confirm_sign_up with the confirmation code to verify the user's email.

To log in a user:
1. Call login_user with the user's email and password to get an access token.
2. Use the access token to authenticate requests to protected endpoints

To delete a user:
1. Call delete_self with the user's access token to delete their account and user data.
'''

import os
import logging

import boto3
from botocore.exceptions import ClientError

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = boto3.client('cognito-idp', region_name='eu-west-2')
dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
user_history_table = dynamodb.Table('c22-fysh-user-data')


def sign_up_user(client_id: str, email: str, password: str):
    '''Sign up a new user with the given email and password.'''
    try:
        response = client.sign_up(
            ClientId=client_id,
            Username=email,
            Password=password,
            UserAttributes=[{'Name': 'email', 'Value': email}]
        )
        logger.info("Sign-up successful! Check your email for a code.")
        return response

    except client.exceptions.UsernameExistsException as e:
        logger.warning("User already exists.")
        raise e
    except client.exceptions.InvalidPasswordException as e:
        logger.warning("Password does not meet complexity requirements.")
        raise e


def confirm_sign_up(client_id: str, email: str, code: str):
    '''Confirm a user's sign-up with the given email and confirmation code.'''
    client.confirm_sign_up(
        ClientId=client_id,
        Username=email,
        ConfirmationCode=code
    )
    logger.info("User confirmed successfully!")


def login_user(client_id: str, email: str, password: str):
    '''Log in a user with the given email and password.'''

    # Attempt to authenticate the user and retrieve an access token
    try:
        response = client.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password
            }
        )
        logger.info("Login successful!")
    except client.exceptions.NotAuthorizedException as e:
        logger.warning("Incorrect username or password.")
        raise e
    except client.exceptions.UserNotConfirmedException as e:
        logger.warning("User is not confirmed yet.")
        raise e

    # If login was successful, add the user to the user history table
    user_sub = get_user_sub(response['AuthenticationResult']['AccessToken'])
    if user_sub:
        add_user_to_user_history(user_sub, email, email.split('@')[0])
        logger.info(f"User {email} added to user history.")

    return response['AuthenticationResult']


def get_user_sub(access_token: str):
    '''Retrieves the user's sub (unique identifier) from Cognito using the access token.'''
    try:
        response = client.get_user(
            AccessToken=access_token
        )
        return response['Username']
    except client.exceptions.NotAuthorizedException:
        logger.warning("Invalid access token.")
        return None


def delete_self(access_token: str) -> None:
    '''Deletes the currently authenticated user based on the provided access token.'''

    # delete user data
    user_sub = get_user_sub(access_token)
    if user_sub:
        delete_user_from_user_history(user_sub)

    # delete user from Cognito
    try:
        client.delete_user(
            AccessToken=access_token
        )
        logger.info("Your account has been deleted.")
    except Exception as e:
        logger.error(f"Delete failed: {e}")


def get_user_from_user_history(user_id: str) -> dict | None:
    """
    Retrieves a user record based on the user_id partition key.
    """
    try:
        response = user_history_table.get_item(Key={'user_id': user_id})
    except ClientError as e:
        logger.error(f"Error fetching user: {e.response['Error']['Message']}")
        return None

    return response.get('Item')


def add_user_to_user_history(user_id: str,
                             email: str,
                             name: str,
                             extra_attributes: dict = None) -> bool:
    """
    Adds a new user to the table. 
    extra_attributes should be a dictionary of any additional fields.
    """
    item = {
        'user_id': user_id,
        'email': email,
        'name': name
    }

    # Merge additional fields if provided
    if extra_attributes:
        item.update(extra_attributes)

    try:
        user_history_table.put_item(Item=item)
        logger.info(f"User {user_id} added successfully.")
        return True
    except ClientError as e:
        logger.error(f"Error adding user: {e.response['Error']['Message']}")
        return False


def delete_user_from_user_history(user_id: str) -> dict | None:
    """
    Deletes a user record based on the user_id.
    """
    try:
        response = user_history_table.delete_item(
            Key={
                'user_id': user_id
            }
        )
        logger.info(f"User {user_id} deleted successfully (or did not exist).")
        return response
    except ClientError as e:
        logger.error(f"An error occurred: {e.response['Error']['Message']}")
        return None


if __name__ == "__main__":
    load_dotenv()
    # I have put an example email and password here,
    # but you should replace these with your own test credentials.
    username = "your_email@example.com"
    password = "Password123!"
    client_id = os.environ['client_id']

    # Sign up a new user
    sign_up_user(client_id, username, password)
    # After receiving the confirmation code via email, confirm the user
    code = input("Enter the confirmation code sent to your email: ")
    confirm_sign_up(client_id, username, code)
    # Log in the user to get an access token
    auth_result = login_user(client_id, username, password)
    # cleanup - delete the user we just created
    if auth_result:
        access_token = auth_result['AccessToken']
        delete_self(access_token)
