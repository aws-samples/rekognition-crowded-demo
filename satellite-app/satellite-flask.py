from flask import Flask, render_template, jsonify, \
    request, Response, redirect, url_for, session
import random
import boto3
import os
import subprocess

# Flask configurations
app = Flask(__name__)
dict_image_rekognition = {'image1' : ['KoreanSatelliteSuperBowl.jpg', 'RekognitionKoreanSatelliteSuperBowl.png'],
                            'image2' : ['ElisIslandNoPeople.png', 'RekognitionElisIslandNoPeople.png']}
key_list = ["image1", "image2"]

@app.route('/')
def hello_world():
    return render_template("sattelite_app.html")

@app.route('/send_image/', methods=['POST'])
def send_image():
    
    print(dict_image_rekognition)

    client = boto3.client('s3')
    bucket_name = os.getenv("BUCKET_NAME","space-enablers-poc")
    bucket_path = ""

    data_path = "static/data"
    # images_on_disk = subprocess.check_output(f"ls -l1 static/data", shell=True)
    # images_list = list(str(images_on_disk).split("\\n"))[:-1]
    random_key = random.choice(key_list)
    random_number = random.randrange(0,300)

    image_name = dict_image_rekognition.get(random_key)[0]
    image_name_rekognition = dict_image_rekognition.get(random_key)[1]

    # Removing the key that is already used
    dict_image_rekognition.pop(random_key, None)
    key_list.remove(random_key)
    try:
        client.upload_file(f"{data_path}/{image_name}", bucket_name, f"input/{random_number}{image_name}")
        return render_template("satellite_return.html", image_path=f"/{data_path}/{image_name}", image_path_rekognition=f"/{data_path}/{image_name_rekognition}")
    except Exception as e:
        raise e

app.run(debug=True, host='0.0.0.0')