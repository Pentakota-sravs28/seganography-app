from flask import Flask, render_template, request, send_file
from PIL import Image
import io

app = Flask(__name__)

def encode_message(image, message):
    binary_message = ''.join(format(ord(i), '08b') for i in message)
    binary_message += '1111111111111110'  # Message delimiter
    
    img = image.convert('RGB')
    pixels = img.load()
    data_index = 0
    message_index = 0
    
    # Loop over each pixel and replace LSB with message bits
    for y in range(img.height):
        for x in range(img.width):
            pixel = list(pixels[x, y])
            for i in range(3):  # Red, Green, Blue channels
                if message_index < len(binary_message):
                    pixel[i] = (pixel[i] & 0xFE) | int(binary_message[message_index])
                    message_index += 1
            pixels[x, y] = tuple(pixel)
            if message_index >= len(binary_message):
                break
        if message_index >= len(binary_message):
            break
    return img

def decode_message(image):
    img = image.convert('RGB')
    pixels = img.load()
    
    binary_message = ''
    
    for y in range(img.height):
        for x in range(img.width):
            pixel = pixels[x, y]
            for i in range(3):  # Red, Green, Blue channels
                binary_message += str(pixel[i] & 1)
    
    # Find the delimiter (1111111111111110)
    delimiter = '1111111111111110'
    message_binary = binary_message.split(delimiter)[0]
    
    message = ''
    for i in range(0, len(message_binary), 8):
        byte = message_binary[i:i+8]
        message += chr(int(byte, 2))
    
    return message

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hide_message', methods=['POST'])
def hide_message():
    image_file = request.files['image']
    message = request.form['message']
    
    image = Image.open(image_file)
    output_image = encode_message(image, message)
    
    img_io = io.BytesIO()
    output_image.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')

@app.route('/extract_message', methods=['POST'])
def extract_message():
    image_file = request.files['image']
    
    image = Image.open(image_file)
    message = decode_message(image)
    
    return message

if __name__ == '__main__':from flask import Flask, render_template, request, send_file, jsonify
import os
import hashlib
import base64
from cryptography.fernet import Fernet
from stegano import lsb
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Function to generate an encryption key
def generate_key(password):
    hashed = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(hashed)

# Function to encrypt a message
def encrypt_message(message, password):
    key = generate_key(password)
    cipher = Fernet(key)
    return cipher.encrypt(message.encode()).decode()

# Function to decrypt a message
def decrypt_message(encrypted_message, password):
    try:
        key = generate_key(password)
        cipher = Fernet(key)
        return cipher.decrypt(encrypted_message.encode()).decode()
    except Exception:
        return "Decryption failed! Wrong password?"


@app.route('/')
def home():
    return render_template('index.html')


@app.route("/encode", methods=["POST"])
def encode():
    if "image" not in request.files or "message" not in request.form or "password" not in request.form:
        return "All fields are required!", 400

    image = request.files["image"]
    message = request.form["message"]
    password = request.form["password"]

    if image.filename == "":
        return "No image selected!", 400

    filename = secure_filename(image.filename)
    img_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    image.save(img_path)

    # Encrypt the message and hide it inside the image
    encrypted_message = "TEXT_ENC:" + encrypt_message(message, password)
    encoded_img = lsb.hide(img_path, encrypted_message)
    
    encoded_img_path = os.path.join(app.config["UPLOAD_FOLDER"], "encoded_image.png")
    encoded_img.save(encoded_img_path)

    return send_file(encoded_img_path, as_attachment=True)

@app.route("/decode", methods=["POST"])
def decode():
    if "image" not in request.files or "password" not in request.form:
        return jsonify({"message": "All fields are required!"}), 400

    image = request.files["image"]
    password = request.form["password"]

    if image.filename == "":
        return jsonify({"message": "No image selected!"}), 400

    filename = secure_filename(image.filename)
    img_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    image.save(img_path)

    try:
        extracted_message = lsb.reveal(img_path)
        if extracted_message and extracted_message.startswith("TEXT_ENC:"):
            decrypted_message = decrypt_message(extracted_message.replace("TEXT_ENC:", "", 1), password)
            return jsonify({"message": decrypted_message})
        else:
            return jsonify({"message": "No valid hidden message found."})
    except Exception as e:
        return jsonify({"message": f"Decoding failed: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)
    app.run(debug=True)
