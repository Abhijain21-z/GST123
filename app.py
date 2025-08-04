#!/usr/bin/env python3
"""
A simple web application with user management and file operations.
This code contains several intentional bugs for demonstration purposes.
"""

import os
import sqlite3
import hashlib
from flask import Flask, request, jsonify, session
import json
import secrets

app = Flask(__name__)
# Fix Bug 1: Use environment variable for secret key with secure fallback
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or secrets.token_hex(32)

# Fix Bug 2: Use parameterized queries to prevent SQL injection
def get_user(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Use parameterized query with ? placeholder
    query = "SELECT * FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    conn.close()
    return result

# Fix Bug 3: Use efficient O(n) algorithm with hash set
def find_duplicates(numbers):
    seen = set()
    duplicates = set()
    
    for num in numbers:
        if num in seen:
            duplicates.add(num)
        else:
            seen.add(num)
    
    return list(duplicates)

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    
    user = get_user(username)
    if user:
        # Simple password check (not secure, but not the main bug we're focusing on)
        stored_password = user[2]  # Assuming password is at index 2
        if password == stored_password:
            session['user'] = username
            return jsonify({'status': 'success'})
    
    return jsonify({'status': 'failed'})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    file = request.files['file']
    filename = file.filename
    
    # Save file to uploads directory
    file.save(f'uploads/{filename}')
    return jsonify({'message': 'File uploaded successfully'})

@app.route('/process_data', methods=['POST'])
def process_data():
    data = request.json.get('numbers', [])
    duplicates = find_duplicates(data)
    return jsonify({'duplicates': duplicates})

if __name__ == '__main__':
    # Create users table
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    
    # Insert test user
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'password123')")
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # User already exists
    
    conn.close()
    
    # Create uploads directory
    os.makedirs('uploads', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0')