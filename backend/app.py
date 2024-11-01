from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from flask import Flask, request, render_template, send_from_directory, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from config.database import get_db_connection
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    create_access_token, create_refresh_token, JWTManager, get_jwt_identity, jwt_required, get_jwt
)

load_dotenv()

app = Flask(__name__)
CORS(app)
# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = os.getenv("MY_SUPER_SECRET")  # Change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

my_email = os.getenv("my_email")
password = os.getenv('password_mail')

# First, let's add a token blocklist set in memory for additional security
blocklist = set()

# Callback to check if the token is in the blocklist
# Add this callback to log token checks (for debugging)
# Callback function to check if a JWT exists in the database blocklist
# Callback function to check if a JWT exists in the database blocklist
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    
    connection = get_db_connection()
    cursor = connection.cursor()

    query = "SELECT id FROM token_blocklist WHERE jti = %s"
    cursor.execute(query, (jti,))
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result is not None


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return render_template('index.html')

@app.route("/api/home")
def home():
    return {
        "msg": "Home"
    }

# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::Authentication routes:::::::::::::::::::::::::::::::::::::::::::::
# Register a user
@app.route('/api/register', methods=['POST'])
def register():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get data from request
        data = request.get_json()

        # Check if email already exists
        cursor.execute('SELECT user_id FROM users WHERE email = %s', (data['email'],))
        if cursor.fetchone():
            return jsonify({'message': 'Email already registered'}), 409

        # Hash the password
        password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')

        # Default role for public registration (e.g., role_id 2 for regular user)
        role_id = 2
        location_id = data.get('location_id', None)  # Optional location_id for new users

        # Insert new user into the database
        cursor.execute('''
            INSERT INTO users (location_id, role_id, first_name, last_name, email, phone, password_hash, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            location_id,
            role_id,
            data['first_name'],
            data['last_name'],
            data['email'],
            data.get('phone'),  # Optional phone number
            password_hash,
            True
        ))

        # Commit the changes to the database
        conn.commit()

        return jsonify({'message': 'User registered successfully'}), 201

    finally:
        cursor.close()
        conn.close()

# Login route
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    # Ensure both email and password are provided
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Fetch user details from the database
        cursor.execute('''
            SELECT u.*, r.name as role_name, l.name as location_name 
            FROM users u 
            JOIN roles r ON u.role_id = r.role_id 
            JOIN locations l ON u.location_id = l.location_id 
            WHERE u.email = %s
        ''', (data['email'],))
        
        user = cursor.fetchone()
        
        # Check if user exists and password matches
        if not user or not bcrypt.check_password_hash(user['password_hash'], data['password']):
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # Check if the account is deactivated
        if not user['is_active']:
            return jsonify({'message': 'Account is deactivated'}), 401
        
        # Generate JWT access and refresh tokens
        access_token = create_access_token(identity=user['user_id'])
        refresh_token = create_refresh_token(identity=user['user_id'])
        
        # Return tokens and user information
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'user_id': user['user_id'],
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'role': user['role_name'],
                'location': user['location_name']
            }
        }), 200
        
    except Exception as e:
        # Log the error or print for debugging
        print(e)
        return jsonify({'message': 'An error occurred during login'}), 500
    
    finally:
        cursor.close()
        conn.close()


# Refresh token route
@app.route("/api/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    token = get_jwt()
    jti = token["jti"]
    iat = token["iat"]  # Extract the "issued at" timestamp from the token
    
    print(f"Refresh attempt - User: {current_user_id}, JTI: {jti}, Issued At: {iat}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Convert 'iat' to a datetime object in UTC
        token_issued_at = datetime.fromtimestamp(iat, tz=timezone.utc)
        
        # Check if user has logged out since this refresh token was issued
        cursor.execute('''
            SELECT EXISTS(
                SELECT 1 FROM user_sessions 
                WHERE user_id = %s 
                AND logout_time > %s
            ) as has_logged_out
        ''', (current_user_id, token_issued_at))  # Compare against the token issuance time
        
        has_logged_out = cursor.fetchone()[0]
        
        if has_logged_out:
            print(f"User {current_user_id} has logged out since refresh token was issued")
            return jsonify({"msg": "Token has been revoked"}), 401
            
        # Check if the token is in memory blocklist
        if jti in blocklist:
            print(f"Token {jti} found in memory blocklist")
            return jsonify({"msg": "Token has been revoked"}), 401
        
        # Check if the token is in the database blocklist
        cursor.execute('SELECT 1 FROM token_blocklist WHERE jti = %s', (jti,))
        if cursor.fetchone():
            print(f"Token {jti} found in database blocklist")
            return jsonify({"msg": "Token has been revoked"}), 401
        
        # If we get here, token is valid, generate new access token
        access_token = create_access_token(identity=current_user_id)
        return jsonify(access_token=access_token)
        
    finally:
        cursor.close()
        conn.close()




# Endpoint for revoking both access and refresh tokens
@app.route("/api/logout", methods=["DELETE"])
@jwt_required(verify_type=False)
def logout():
    token = get_jwt()
    jti = token["jti"]
    ttype = token["type"]  # Access or refresh
    user_id = get_jwt_identity()
    now = datetime.now(timezone.utc)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Add current token to memory blocklist
        blocklist.add(jti)

        # 2. Add the current token (access or refresh) to the database blocklist
        cursor.execute(
            'INSERT INTO token_blocklist (jti, type, created_at, user_id) VALUES (%s, %s, %s, %s)',
            (jti, ttype, now, user_id)
        )

        # 3. If it's an access token, also try to revoke the refresh token
        if ttype == "access":
            # Extract the refresh token from the custom header (or handle this on the frontend)
            auth_header = request.headers.get('X-Refresh-Token')
            if auth_header and auth_header.startswith('Bearer '):
                refresh_token = auth_header.split(' ')[1]
                try:
                    # Decode the refresh token to get its JTI
                    decoded_token = jwt.decode_token(refresh_token)
                    refresh_jti = decoded_token["jti"]

                    # Add the refresh token to memory and database blocklist
                    blocklist.add(refresh_jti)
                    cursor.execute(
                        'INSERT INTO token_blocklist (jti, type, created_at, user_id) VALUES (%s, %s, %s, %s)',
                        (refresh_jti, 'refresh', now, user_id)
                    )
                except Exception as e:
                    print(f"Error processing refresh token: {e}")

            # Record the logout in the user_sessions table
            cursor.execute(
                'INSERT INTO user_sessions (user_id, logout_time) VALUES (%s, %s)',
                (user_id, now)
            )

        conn.commit()
        return jsonify(msg=f"Logged out successfully. Token type: {ttype}"), 200

    except Exception as e:
        conn.rollback()
        print(f"Logout error: {e}")
        return jsonify(msg="Error during logout", error=str(e)), 500

    finally:
        cursor.close()
        conn.close()


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::End of authentication:::::::::::::::::::::::::::::::::::::::::::::






# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::Test routes:::::::::::::::::::::::::::::::::::::::::::::::::::::::::
@app.route("/api/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(message=f"You have accessed a protected route, {current_user}!")

# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::End of test:::::::::::::::::::::::::::::::::::::::::::::::::::::::::



@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.json
    message = data['message']
    name = data["name"]
    email = data["email"]
    
    msg = MIMEMultipart()
    msg['To'] = email
    msg['Subject'] = "Hello"
    msg['From'] = email

    body = f"Name: {name}, Email: {email}, Message: {message}"
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as connection:
            connection.starttls()
            connection.login(my_email, password)
            connection.sendmail(my_email, my_email, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
        return {
            "error": "Mail not sent"
        }
    return {
        "msg": "Contact"
    }, 200


if __name__=="__main__":
    app.run(port=5000, debug=True, host='0.0.0.0')
