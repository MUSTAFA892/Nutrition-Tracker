import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import google.generativeai as genai
from PIL import Image
import base64
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from urllib.parse import urlparse, urljoin
from bson.objectid import ObjectId
from datetime import datetime

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Set secret key for session management
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Set the maximum content length for file uploads (e.g., 16MB)
app.config['MAX_CONTENT_LENGTH'] = 5000 # 16MB limit

# MongoDB configuration (URI provided in .env)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)

# Initialize Bcrypt for password hashing
bcrypt = Bcrypt(app)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Redirect to login if not authenticated

# Set the upload folder and allowed extensions
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# User model for login functionality
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if user:
        return User(str(user['_id']))
    return None

# Check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to interact with the Gemini API
def get_gemini_response(input_text, image, prompt):
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content([input_text, image[0], prompt])
    return response.text

# Error handler for file too large
@app.errorhandler(413)
def request_entity_too_large(error):
    flash("File is too large. Please upload a smaller file.", "danger")
    return redirect(request.url)  # Redirect back to the page

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the user exists in the database
        user = mongo.db.users.find_one({"username": username})

        if user and bcrypt.check_password_hash(user['password'], password):
            # User found and password is correct
            login_user(User(str(user['_id'])))

            # Handle `next` parameter for redirection
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != "":
                next_page = url_for('index')  # Redirect to the index page
            return redirect(next_page)
        else:
            flash("Invalid username or password!", "danger")

    return render_template('login.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Check if the username already exists
        if mongo.db.users.find_one({"username": username}):
            flash("Username already exists!", "danger")
        else:
            mongo.db.users.insert_one({"username": username, "password": hashed_password})
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    image_path = None
    history = []  # To store the history of searches

    # Fetch the history from MongoDB
    history = mongo.db.history.find({"user_id": current_user.id})  # Filter by user

    if request.method == "POST":
        # Check if image file or captured image was provided
        image_file = request.files.get('image')
        captured_image = request.form.get('captured_image')

        # Check if an image file is uploaded
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(filepath)
            image_path = filepath
        # Check if a captured image (base64) is provided
        elif captured_image:
            try:
                image_data = base64.b64decode(captured_image.split(',')[1])
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'captured_image.png')
                with open(image_path, 'wb') as img_file:
                    img_file.write(image_data)
            except Exception as e:
                flash(f"Error while processing the captured image: {str(e)}", "danger")

        # If an image path is created, process it
        if image_path:
            try:
                # Open the image using PIL (to check if the image is valid)
                Image.open(image_path)

                # Get the user input text
                input_text = request.form.get('input_text', '')

                # Prepare the image data for the API call
                image_parts = [{
                    "mime_type": "image/png",
                    "data": open(image_path, "rb").read()
                }]

                # Prepare the prompt for the API
                input_prompt = """
            You are an expert in nutrition. You are given an image of food items. For each food item, calculate the following nutritional details:

            - Total calories
            - Protein
            - Carbohydrates
            - Fats
            - Fiber

            Provide the nutritional breakdown for each item in the following format:

            1. Item 1 - Calories: X, Protein: Yg, Carbs: Zg, Fats: Wg, Fiber: Vg
            2. Item 2 - Calories: A, Protein: Bg, Carbs: Cg, Fats: Dg, Fiber: Eg

            ----

            Then, calculate the overall total of the following nutrients from all items combined:
            - Total Calories
            - Total Protein
            - Total Carbs
            - Total Fats
            - Total Fiber

            Provide the result in this format:

            Total Calories: T
            Total Protein: Pg
            Total Carbs: Cg
            Total Fats: Dg
            Total Fiber: Eg


            Example- 
            1. Roasted Chicken (3-4oz cooked without skin) - Calories: 165, Protein: 30g, Carbs: 0g, Fats: 7g, Fiber: 0g

            
            Total Calories: 165
            Total Protein: 30g
            Total Carbs: 0g
            Total Fats: 7g
            Total Fiber: 0g

            Note: Please provide the nutritional details for each food like in the above example.note that i want each output like the above example and not other paragraph or text.
            Also give me the response very fast within 1 minute.
                """

                # Call Gemini API to get the response
                response_text = get_gemini_response(input_text, image_parts, input_prompt)

                # Store the result in MongoDB (history)
                mongo.db.history.insert_one({
                    "user_id": current_user.id,
                    "image_path": image_path,
                    "response": response_text,
                    "timestamp": datetime.utcnow()
                })

                # Render the result on the page
                return render_template('index.html', response=response_text, image_path=image_path, history=history)

            except Exception as e:
                flash(f"Error while processing the image: {str(e)}", "danger")
                return render_template('index.html', response=None, history=history)

        else:
            flash("Please upload a valid image or provide a captured image.", "danger")
            return render_template('index.html', response=None, history=history)

    return render_template('index.html', response=None, history=history)


@app.route("/history")
@login_required
def history():
    # Fetch the history from MongoDB
    history = mongo.db.history.find({"user_id": current_user.id})  # Filter by user
    return render_template('history.html', history=history)

@app.route('/delete_history', methods=['POST'])
def delete_history():
    if current_user.is_authenticated:
        # Delete all history entries for the current user
        mongo.db.history.delete_many({"user_id": current_user.id})  # Delete history from MongoDB for this user
        
        flash("Your search history has been deleted successfully.", "success")
        return redirect(url_for('history'))  # Redirect back to the history page
    else:
        flash("You need to be logged in to delete history.", "danger")
        return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
