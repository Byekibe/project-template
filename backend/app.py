from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from flask import Flask, request, render_template, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

my_email = os.getenv("my_email")
password = os.getenv('password_mail')

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
