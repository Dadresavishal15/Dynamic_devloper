from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

import os
import random

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:newpassword@localhost:5432/daiict'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24) # Required for session handling
db = SQLAlchemy(app)

# User model
class users(db.Model):
    __tablename__ = 'users'  # Name of the table you created in PostgreSQL
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    mobile_number = db.Column(db.String(15), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
# Book model
class Book(db.Model):
    __tablename__ = 'books'
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255))
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    image_url = db.Column(db.String(255))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        mobile_number = request.form['mobile_number']
        # Check if the user already exists
        existing_user = users.query.filter_by(email=email).first()

        if existing_user:
            flash('Email already exists. Please choose a different email or log in.')
            return redirect(url_for('signup'))

        # Create a new user and store in the database
        new_user = users(username=username, email=email, mobile_number = mobile_number)
        new_user.set_password(password)  # Store hashed password

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! Please log in.')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating account: {str(e)}')
            return redirect(url_for('signup'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        mobile_number = request.form['mobile_no']

        # Check if the user exists
        usere = users.query.filter_by(email=email).first()
        userm = users.query.filter_by(mobile_number=mobile_number).first()

        if (usere and usere.check_password(password)) or (userm and userm.check_password(password)):
            session['username'] = usere.username if usere else userm.username
            session['mobile_no'] = usere.mobile_no if usere else userm.mobile_no
            flash('Login successful!')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password. Please try again.')

    return render_template('login.html')

@app.route('/')
def index():
    # # Fetch a random selection of books (let's say 5 random books)
    # books = Book.query.order_by(db.func.random()).limit(5).all()
    return render_template('index.html')

@app.route('/catalog')
def catalog():
    return render_template('catalog.html')

if __name__ == '__main__':
    app.run(debug=True)
