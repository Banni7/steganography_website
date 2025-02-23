from flask import Flask, render_template, request
import cv2
import os
import numpy as np

app = Flask(__name__)

# Define output folder
OUTPUT_FOLDER = "static/output/"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/encrypt", methods=["POST"])
def encrypt():
    if "image" not in request.files:
        return render_template("index.html", encrypted_result="❌ No file selected!", decrypted_result="")

    image = request.files["image"]
    message = request.form["message"]
    password = request.form["password"]

    if image.filename == "":
        return render_template("index.html", encrypted_result="❌ No file selected!", decrypted_result="")

    # Read image
    img_array = np.frombuffer(image.read(), np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    n, m, z = 0, 0, 0

    # Store password with a separator (*)
    for char in password + "*":
        img[n, m, z] = ord(char) % 256
        z = (z + 1) % 3
        if z == 0:
            m += 1
        if m >= img.shape[1]:  
            m = 0
            n += 1

    # Store message with separator (#)
    for char in message + "#":
        img[n, m, z] = ord(char) % 256
        z = (z + 1) % 3
        if z == 0:
            m += 1
        if m >= img.shape[1]:  
            m = 0
            n += 1

    # Save encrypted image
    encrypted_path = os.path.join(OUTPUT_FOLDER, "encrypted_" + image.filename)
    cv2.imwrite(encrypted_path, img)

    return render_template("index.html", encrypted_result=f"✅ Encryption successful! <a href='/{encrypted_path}' download>Download Image</a>", decrypted_result="")

@app.route("/decrypt", methods=["POST"])
def decrypt():
    if "image" not in request.files:
        return render_template("index.html", encrypted_result="", decrypted_result="❌ No file selected!")

    image = request.files["image"]
    password_input = request.form["password"]

    if image.filename == "":
        return render_template("index.html", encrypted_result="", decrypted_result="❌ No file selected!")

    # Read image
    img_array = np.frombuffer(image.read(), np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    n, m, z = 0, 0, 0
    retrieved_password = ""
    retrieved_message = ""

    # Extract password
    while True:
        char = chr(img[n, m, z])
        if char == "*":
            break
        retrieved_password += char
        z = (z + 1) % 3
        if z == 0:
            m += 1
        if m >= img.shape[1]:  
            m = 0
            n += 1

    # Move past separator
    z = (z + 1) % 3
    if z == 0:
        m += 1
    if m >= img.shape[1]:  
        m = 0
        n += 1

    # Extract message
    while True:
        char = chr(img[n, m, z])
        if char == "#":
            break
        retrieved_message += char
        z = (z + 1) % 3
        if z == 0:
            m += 1
        if m >= img.shape[1]:  
            m = 0
            n += 1

    if password_input == retrieved_password:
        return render_template("index.html", encrypted_result="", decrypted_result=f"✅ Decryption successful! Message: <b>{retrieved_message}</b>")
    else:
        return render_template("index.html", encrypted_result="", decrypted_result="❌ Incorrect password!")

if __name__ == "__main__":
    app.run(debug=True)
