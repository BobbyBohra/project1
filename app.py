from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from tensorflow.keras.models import load_model
import numpy as np
from PIL import Image
import os
import traceback

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this in production

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Load your ML model once when app starts
try:
    model = load_model('animal_model.keras')
    print("Model loaded successfully.")
except Exception as e:
    print("Error loading model:", e)
    model = None

class_names = ['Bear', 'Bird', 'Cat', 'Cow', 'Deer', 'Dog', 'Dolphin', 'Elephant', 'Giraffe',
               'Horse', 'Kangaroo', 'Lion', 'Panda', 'Tiger', 'Zebra']

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('User already exists. Please login.')
            return redirect(url_for('login'))
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.')
    return render_template('open.html')

@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    try:
        if model is None:
            flash("Model not loaded. Cannot make predictions.")
            return redirect(url_for('dashboard'))

        if 'image' not in request.files or request.files['image'].filename == '':
            flash("No file uploaded.")
            return redirect(url_for('dashboard'))

        image_file = request.files['image']

        img = Image.open(image_file).resize((224, 224)).convert('RGB')
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        preds = model.predict(img_array)[0]  # Get predictions for single image
        top_indices = preds.argsort()[-3:][::-1]  # Top 3 prediction indices
        top_preds = [(class_names[i], float(preds[i])) for i in top_indices]

        # Example top_preds: [('Tiger', 0.85), ('Lion', 0.10), ('Cat', 0.05)]

        return render_template('dashboard.html', name=current_user.username, top_preds=top_preds)

    except Exception as e:
        error_msg = traceback.format_exc()
        print("Error during prediction:\n", error_msg)
        flash("Error during prediction. Please check server logs.")
        return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    if not os.path.exists('users.db'):
        with app.app_context():
            db.create_all()
    app.run(debug=True)
