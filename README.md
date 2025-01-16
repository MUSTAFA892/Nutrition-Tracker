

# Nutrition Tracker

This is a Flask-based web application for calculating nutritional information from images of food items. Users can upload food images or capture photos using their mobile devices. The app uses Google's Gemini API for extracting nutritional details from food images.

## Features

- User Registration and Login: Users can create an account, log in, and manage their sessions.
- Image Upload: Users can upload images of food items.
- Photo Capture: Users can capture photos using their mobile devices and submit them for analysis.
- Nutritional Information Extraction: The app interacts with Google Gemini API to extract detailed nutritional information (calories, protein, carbohydrates, fats, fiber, etc.) from the food items in the images.
- History Tracking: Users' search history, including the uploaded images and the API responses, is saved and can be viewed.
- History Deletion: Users can delete their search history.

## Technologies Used

- **Backend**: Flask, Python
- **Database**: MongoDB
- **Authentication**: Flask-Login, Flask-Bcrypt
- **Image Processing**: Pillow (PIL)
- **API**: Google Gemini API for generating content based on food images
- **Frontend**: HTML, CSS (Custom styles)

## Installation

To run this project locally, follow the steps below:

1. **Clone the repository**:

   ```bash
   git clone https://github.com/MUSTAFA892/Nutrition-Tracker.git
   cd Nutrition-Tracker
   ```

2. **Create a virtual environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the required dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file** in the root directory and add your environment variables:

   ```plaintext
   FLASK_SECRET_KEY=your_secret_key
   MONGO_URI=your_mongodb_connection_uri
   GOOGLE_API_KEY=your_google_api_key
   ```

5. **Run the application**:

   ```bash
   python app.py
   ```

   The app will be available at `http://127.0.0.1:5000` by default.

## Deployment

To deploy the application, you can use cloud platforms like [Render](https://render.com/), [Heroku](https://heroku.com/), or any other that supports Python applications with MongoDB.

### Deployment on Render

1. Create a Render account and log in.
2. Create a new Web Service.
3. Connect your GitHub repository to Render.
4. Set environment variables in Render (FLASK_SECRET_KEY, MONGO_URI, GOOGLE_API_KEY).
5. Deploy the app and access it through the provided URL.

## File Structure

```plaintext
Nutrition-Tracker/
│
├── app.py                # Main application logic
├── .gitignore            # Ignore .env and other unwanted files
├── requirements.txt      # Project dependencies
├── static/
│   └── uploads/          # Folder where uploaded images are stored
└── templates/
    ├── index.html        # Main page template
    ├── login.html        # Login page template
    ├── register.html     # Registration page template
    └── history.html      # History page template
```

## Environment Variables

- `FLASK_SECRET_KEY`: Secret key for Flask session management.
- `MONGO_URI`: MongoDB connection URI.
- `GOOGLE_API_KEY`: API key for Google's Gemini API.

## Contributing

Feel free to fork the repository, make changes, and submit pull requests. Please ensure that your code follows the PEP8 guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

---

### Notes:
- Replace the placeholders like `your_secret_key`, `your_mongodb_connection_uri`, and `your_google_api_key` with actual values.
- If you plan to deploy it on a specific platform (Render, Heroku, etc.), you might need to adjust deployment instructions based on the platform.

This `README.md` should provide a solid foundation for documenting your project. You can further expand it based on any additional features or configurations you have in the app.