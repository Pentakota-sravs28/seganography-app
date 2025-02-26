Imagesteganography
A web-based steganography application that allows users to hide and retrieve secret messages in images using the Least Significant Bit (LSB) technique. The backend is built with Python (Flask), while the frontend uses HTML, CSS, and JavaScript.

Project Structure
│   app.py                 # Flask backend for encoding/decoding messages
│   README.md              # Project documentation
│   requirements.txt       # Dependencies list
│
├───static                 # Static frontend assets
│   │   script.js          # Handles UI interactions and API calls
│   │   style.css          # Styling for the web interface
│   │
│   └───uploads            # Stores encoded images
│           encoded_image.png
│           encoded_image_2.png
│           Screenshot_2023-12-25_192907.png
│
├───templates              # HTML templates for Flask
│       index.html         # Main web interface
│
└───uploads                # Directory to save user-uploaded images
