from flask import Flask, jsonify, request, send_from_directory
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='websiteFiles', static_url_path='') # location of website files

# serve static website files
@app.route('/')
def serveIndex():
    return send_from_directory(app.static_folder, 'index.html')

# add new review to reviews.json
@app.route('/submit-review', methods=['POST'])
def makeReview():
    parkId = request.form.get('parkName').lower().strip(' ')
    star = int(request.form.get('star'))
    text = request.form.get('text')

    newReview = {
        "parkId": parkId,
        "stars" : star,
        "text": text
    }

    with open("websiteFiles/data/reviews.json",'r+') as file:
        fileData = json.load(file)
        fileData.append(newReview)
        file.seek(0)
        json.dump(fileData, file, indent = 4)

    return 'Park submitted successfully!'

# add new park to parks.json
@app.route('/submit-park', methods=['POST'])
def addPark():
    parkName = request.form.get('parkName')
    latLong = request.form.get('latLong')
    latitude, longitude = map(float, latLong.split(',')) # get seperated values
    isPark = 'isPark' in request.form
    isTrail = 'isTrail' in request.form
    tagsString = request.form.get('tags', '')
    tags = tagsString.split(',') # get list of all tags

    newPark = {
        "id": parkName.lower().strip(' '),
        "name": parkName,
        "location": {
            "longitude": longitude,
            "latitude": latitude
        },
        "tags": tags
    }

    with open("websiteFiles/data/parks.json",'r+') as file:
        fileData = json.load(file)
        fileData.append(newPark)
        file.seek(0)
        json.dump(fileData, file, indent = 4)

    # Save uploaded images
    imageFolder = os.path.join(app.static_folder,'data/photos')

    uploaded_files = request.files.getlist('uploadFile')
    for i, image in enumerate(uploaded_files):
        ext = os.path.splitext(image.filename)[1]
        filename = f"{parkName.lower().strip(' ')}-{chr(97+i)}{ext}"  # a, b, c, ...
        image.save(os.path.join(imageFolder, secure_filename(filename)))
        print("hello")

    return 'Park submitted successfully!'

if __name__ == '__main__':
    app.run(debug=True, port=3000)