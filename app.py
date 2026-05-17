import os
import re
import pytesseract
import cv2
import numpy as np
from flask import Flask, request, render_template, jsonify, send_file
from PIL import Image
from werkzeug.utils import secure_filename

import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

correct_fields = [
    "Passport Number", "Control Number", "Issuing Post Name", "Surname",
    "Sex", "Birth Date", "Issue Date", "Expiration Date"
]

def preprocess_image(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return Image.fromarray(image)

def extract_text(image):
    image = preprocess_image(image)
    return pytesseract.image_to_string(image)

def extract_fields_using_regex(raw_text):
    extracted_data = {}

    num_sequences = re.findall(r'\b\d+\b', raw_text)
    if num_sequences:
        extracted_data["Control Number"] = max(num_sequences, key=len)

    issuing_post_match = re.search(r"Issuing\s*Post\s*Name\s*([A-Za-z\s]+)", raw_text)
    if issuing_post_match:
        extracted_data["Issuing Post Name"] = issuing_post_match.group(1).strip()

    surname_match = re.search(r"Surname\s*([\w]+)", raw_text)
    if surname_match:
        extracted_data["Surname"] = surname_match.group(1).strip()

    sex_match = re.search(r"\b([MF])\b", raw_text)
    if sex_match:
        extracted_data["Sex"] = sex_match.group(1).strip()

    date_matches = re.findall(r'\d{2}[A-Z]{3}\d{4}', raw_text)

    if date_matches:
        extracted_data["Birth Date"] = date_matches[0]
        if len(date_matches) > 1:
            extracted_data["Issue Date"] = date_matches[-2]
            extracted_data["Expiration Date"] = date_matches[-1]

    return extracted_data

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    image = cv2.imread(file_path)
    raw_text = extract_text(image)
    extracted_data = extract_fields_using_regex(raw_text)

    output_file = os.path.join(OUTPUT_FOLDER, f"{filename}.txt")
    with open(output_file, "w") as f:
        for key in correct_fields:
            f.write(f"{key}: {extracted_data.get(key, 'Not Found')}\n")

    return jsonify({"extracted_data": extracted_data, "download_link": f"/download/{filename}.txt"})

@app.route("/download/<filename>")
def download(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)