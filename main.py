from flask import Flask, render_template, request, jsonify, redirect
import os
import cv2
import sqlite3
import numpy as np
import base64


currentlocation=os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
def apply_grayscale_filter(image):
    # Convert the image to grayscale using OpenCV
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Convert the grayscale image back to BGR color space to have 3 channels like the original image
    result_image = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)
    return result_image


def apply_brightness_filter(image, brightness_value):
    # Convert the brightness_value to the range of -255 to 255
    brightness_value = int(map_value(brightness_value, 0, 100, -255, 255))

    # Apply brightness adjustment using OpenCV
    if brightness_value != 0:
        if brightness_value > 0:
            shadow = brightness_value
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness_value
        alpha_b = (highlight - shadow) / 255
        gamma_b = shadow
        result_img = cv2.addWeighted(image, alpha_b, image, 0, gamma_b)
    else:
        result_img = image.copy()

    return result_img


def map_value(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def apply_saturation_filter(image, saturation_value):
    # Convert the image to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Apply the saturation adjustment
    hsv[..., 1] = hsv[..., 1] + saturation_value

    # Convert the image back to BGR color space
    result_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return result_image


def apply_text_to_image(image, text, position=(10, 30), font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=1, color=(255, 255, 255), thickness=2):
    # Add text to the image using OpenCV
    result_image = image.copy()
    cv2.putText(result_image, text, position, font, font_scale, color, thickness)
    return result_image
    
@app.route('/process_image', methods=['POST'])
def process_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    image_data = file.read()
    image_array = cv2.imdecode(np.frombuffer(image_data, np.uint8), -1)

    # Check if the 'filter' parameter is present in the request
    filter_name = request.form.get('filter', '').lower()

    # Check if the 'value' parameter is present in the request
    filter_value = int(request.form.get('value', 0))

    # Apply the specified filter to the image
    if filter_name == 'grayscale':
        processed_image = apply_grayscale_filter(image_array)
    elif filter_name == 'brightness':
        processed_image = apply_brightness_filter(image_array, filter_value)
    elif filter_name == 'saturation':
        processed_image = apply_saturation_filter(image_array, filter_value)
    else:
        # If no filter is specified or the filter is not recognized, return the original image
        processed_image = image_array

    # Encode the processed image to base64
    retval, buffer = cv2.imencode('.jpg', processed_image)
    encoded_image = base64.b64encode(buffer).decode('utf-8')

    return jsonify({'encoded_image': encoded_image})
# Route for serving index.html at the root URL
@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')
@app.route("/login",methods=["POST"])
def checklogin():
    UN=request.form['Username']
    PW=request.form['Password']

    sqlconnection=sqlite3.Connection(currentlocation+"\Login.db")

    cursor=sqlconnection.cursor()
    query1="SELECT Username,Password From Users WHERE Username={un} AND Password={pw}".format(un=UN,pw=PW)
    rows=cursor.execute(query1)
    rows=rows.fetchall()
    if len(rows)==1:
        return redirect ("/index.html")
    else:
        return redirect("/register")

        
@app.route('/rotate_image', methods=['POST'])
def rotate_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    image_data = file.read()
    image_array = cv2.imdecode(np.frombuffer(image_data, np.uint8), -1)

    # Check if the 'angle' parameter is present in the request
    angle = int(request.form.get('angle', 0))

    # Apply rotation to the image
    processed_image = apply_rotation(image_array, angle)

    # Encode the processed image to base64
    retval, buffer = cv2.imencode('.jpg', processed_image)
    encoded_image = base64.b64encode(buffer).decode('utf-8')

    return jsonify({'encoded_image': encoded_image})

@app.route("/register",methods=["GET","POST"])
def registerpage():
    if request.method=="POST":
        dUN=request.form['DUsername']
        dPW=request.form['DPassword']
        Uemail=request.form['EmalUser']
        sqlconnection=sqlite3.Connection(currentlocation+"\Login.db")
        cursor=sqlconnection.cursor()
        query1="INSERT INTO Users VALUES('{u}','{p}','{e}')".format(u=dUN,p=dPW,e=Uemail)
        cursor.execute(query1)
        sqlconnection.commit()
        return redirect("/index.html")
    return render_template("register.html")

@app.route("/logout")

def logout():
    
    return redirect("/ind2.html")

def create_table():
    conn = sqlite3.connect('Login.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
                        Username TEXT NOT NULL,
                        Password TEXT NOT NULL,
                        Email TEXT NOT NULL
                    )''')
    conn.commit()
    conn.close()




# Define your Flask routes here
@app.route('/<template_name>')
def render_template_file(template_name):
    if template_name.endswith('.html') or template_name.endswith('.js'):
        template_path = os.path.join('templates', template_name)
        if os.path.exists(template_path):
            return render_template(template_name)
    return "Template not found", 404


if __name__ == "__main__":
    create_table()  # Call the function to create the table before running the app

    app.run(debug=False,host='0.0.0.0')
