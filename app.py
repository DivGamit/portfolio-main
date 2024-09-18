from flask import Flask, render_template, send_from_directory, abort, request, jsonify
from flask_pymongo import PyMongo
import os
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure MongoDB URI using environment variables
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/portfolio')
mongo = PyMongo(app)

# Define the static folder path
STATIC_FOLDER = 'static'

def is_valid_email(email):
    email_regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(email_regex, email)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    # Serve files from the 'static' folder
    try:
        return send_from_directory(STATIC_FOLDER, filename, as_attachment=True)
    except FileNotFoundError:
        abort(404, description="File not found.")

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('sender-name')
    email = request.form.get('sender-email')
    message = request.form.get('message')

    if not name or not email or not message:
        abort(400, description="All fields are required.")
    
    if not is_valid_email(email):
        abort(400, description="Invalid email address.")

    data = {
        'name': name,
        'email': email,
        'message': message
    }
    
    try:
        mongo.db.contacts.insert_one(data)
    except Exception as e:
        app.logger.error(f"Error inserting data into MongoDB: {e}")
        abort(500, description="Error processing your request. Please try again later.")
    
    return jsonify({"message": "Form submitted successfully!"}), 200

if __name__ == '__main__':
    app.run(debug=True)

