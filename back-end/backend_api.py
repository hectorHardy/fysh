import os

from flask import Flask, request, jsonify
from flask_cors import CORS


import authentication as auth_logic

app = Flask(__name__)
CORS(app)  # Enable CORS so your frontend can talk to the backend

CLIENT_ID = os.environ.get('CLIENT_ID')


@app.route('/signup', methods=['POST'])
def signup():
    '''Handles user signup by accepting email and password, then calling the authentication logic.'''
    data = request.json
    email = data.get('email')
    password = data.get('password')

    try:
        response = auth_logic.sign_up_user(CLIENT_ID, email, password)
        if response:
            return jsonify({"message": "User created, check email"}), 201

    except auth_logic.client.exceptions.UsernameExistsException:
        return jsonify({"error": "User already exists"}), 400
    except auth_logic.client.exceptions.InvalidPasswordException:
        return jsonify({"error": "Password does not meet complexity requirements"}), 400
    except Exception as e:
        app.logger.error(f"Unexpected error during signup: {e}")
        return jsonify({"error": "Signup failed, please try again."}), 400


@app.route('/confirm', methods=['POST'])
def confirm():
    '''Handles user confirmation by accepting email and confirmation code, then calling the authentication logic.'''
    data = request.json
    email = data.get('email')
    code = data.get('code')

    try:
        auth_logic.confirm_sign_up(CLIENT_ID, email, code)
        return jsonify({"message": "Confirmed"}), 200

    except auth_logic.client.exceptions.CodeMismatchException:
        return jsonify({"error": "Invalid verification code"}), 400
    except auth_logic.client.exceptions.ExpiredCodeException:
        return jsonify({"error": "Verification code expired"}), 400
    except Exception as e:
        app.logger.error(f"Unexpected error during confirmation: {e}")
        return jsonify({"error": "Confirmation failed, please try again."}), 400


@app.route('/login', methods=['POST'])
def login():
    '''Handles user login by accepting email and password, then calling the authentication logic.'''
    try:
        auth_result = auth_logic.login_user(
            CLIENT_ID, request.json['email'], request.json['password'])

        # Only send what the frontend actually needs
        return jsonify({
            "access_token": auth_result['AccessToken'],
            "id_token": auth_result['IdToken'],
            "expires_in": auth_result['ExpiresIn'],
            # "refresh_token": auth_result['RefreshToken'] # Consider keeping this in a cookie instead!
        }), 200
    except auth_logic.client.exceptions.NotAuthorizedException:
        return jsonify({"error": "Incorrect username or password"}), 401
    except auth_logic.client.exceptions.UserNotConfirmedException:
        return jsonify({"error": "User is not confirmed yet"}), 401
    except auth_logic.client.exceptions.UserNotFoundException:
        return jsonify({"error": "User not found"}), 400
    except Exception as e:
        # Log the actual error for debugging
        app.logger.error(f"Unexpected error during login: {e}")
        return jsonify({"error": "Something went wrong. Please try again later"}), 401


@app.route('/get-user-name', methods=['GET'])
def get_user_name():
    '''Fetch the username based on the access token provided in the request.'''
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization header missing or invalid"}), 401

    # Extract the token after "Bearer"
    access_token = auth_header.split(' ')[1]
    # Get the user ID from the token
    user_id = auth_logic.get_user_sub(access_token)

    if not user_id:
        return jsonify({"error": "Invalid or expired token"}), 401

    user_data = auth_logic.get_user_from_user_history(
        user_id)  # Fetch user data from DynamoDB
    if not user_data:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"name": user_data.get('name')}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
