import os
from dotenv import load_dotenv
import authentication

load_dotenv()
CLIENT_ID = os.environ.get('client_id')

if __name__ == "__main__":
    # This is just a quick script to delete the user we created for testing purposes.
    # In a real application, you would never want to do this, but it can be useful during development.
    email = "trainee.connor.calkin@sigmalabs.co.uk"
    password = "Password!123"
    response = authentication.login_user(
        CLIENT_ID, email, password)
    if response:
        delete_response = authentication.delete_self(response['AccessToken'])
        print(delete_response)
    else:
        print("Login failed, cannot delete user.")
