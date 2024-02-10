from flask import Flask, request, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity


app = Flask(__name__)

# Configure Flask-JWT-Extended
app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Change this to a secure secret key
jwt = JWTManager(app)

# MongoDB connection
client = MongoClient('mongodb+srv://harshal:harshalxyz@cluster0.q32myeh.mongodb.net/task_manager_db?retryWrites=true&w=majority')
db = client.task_manager_db

@app.route('/')
def home():
    return '<h1>Welcome to the Task Manager App!</h1>'

# User registration route
@app.route('/api/users/register', methods=['POST'])
def register_user():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Check if the username or email already exists in the database
    if db.users.find_one({'$or': [{'username': username}, {'email': email}]}):
        return jsonify({'error': 'Username or email already exists'}), 400

    # Hash the password before storing it in the database
    hashed_password = generate_password_hash(password)

    # Create a new user document
    user = {
        'username': username,
        'email': email,
        'password': hashed_password
    }

    # Insert the user document into the database
    db.users.insert_one(user)
    return jsonify({'message': 'User registered successfully'}), 201


# User login route
@app.route('/api/users/login', methods=['POST'])
def login_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Find the user document in the database by username
    user = db.users.find_one({'username': username})

    # Check if the user exists and the password is correct
    if user and check_password_hash(user['password'], password):
        # Generate JWT token
        access_token = create_access_token(identity=username)

          # Convert ObjectId to string for JSON serialization
        user['_id'] = str(user['_id'])

        # Include user data and access token in the response
        response_data = {
            'user': user,
            'access_token': access_token
        }
        return jsonify(response_data), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

if __name__ == '__main__':
    app.run(debug=True)


# Task model
@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.json
    task = {
        'title': data['title'],
        'description': data['description'],
        'due_date': data['due_date'],
        'user_id': data['user_id'],
        # Add more fields as needed
    }
    db.tasks.insert_one(task)
    return jsonify({'message': 'Task created successfully'}), 201

if __name__ == '__main__':
    app.run(debug=True)


