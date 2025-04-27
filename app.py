from flask import Flask, jsonify, request, send_from_directory, redirect
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
    # get relevant info
    parkId = request.form.get('parkName').lower().replace(" ","")
    star = int(request.form.get('star'))
    text = request.form.get('text')

    # JSON format of review
    newReview = {
        "parkId": parkId,
        "stars" : star,
        "text": text
    }

    # write in review to reviews.json
    with open("websiteFiles/data/reviews.json",'r+') as file:
        fileData = json.load(file)
        fileData.append(newReview)
        file.seek(0)
        json.dump(fileData, file, indent = 4) # turn back into JSON

    # update rating value in parks.json
    with open("websiteFiles/data/parks.json",'r+') as file:
        fileData = json.load(file)

        for park in fileData:
            if (park["id"] == parkId): # find park with same id in parks.json
                amount = park["rating"]["amount"] + 1
                weight = park["rating"]["weight"] + star # calculate new weight
                
                park["rating"]["value"] = weight / amount # get new average
                park["rating"]["amount"] = amount
                park["rating"]["weight"] = weight
            
            file.seek(0)
            json.dump(fileData, file, indent = 4) # turn back into JSON
            file.truncate() # make sure data is updated

    return 'Review submitted successfully!'


# add new park to parks.json
@app.route('/submit-park', methods=['POST'])
def addPark():
    # grab variables
    parkName = request.form.get('parkName')
    id = parkName.lower().replace(" ","")
    latLong = request.form.get('latLong')
    latitude, longitude = map(float, latLong.split(',')) # get seperated values
    isPark = int('isPark' in request.form)
    isTrail = int('isTrail' in request.form)
    if (request.form.get('isPark') and request.form.get('isTrail')):
        type = "both"
    elif (request.form.get('isPark')):
        type = "park"
    else:
        type = "trail"
    tagsString = request.form.get('tags', '')
    tags = tagsString.split(',') # get list of all tags

    # JSON format of park
    newPark = {
        "id": id,
        "name": parkName,
        "location": {
            "longitude": longitude,
            "latitude": latitude
        },
        "tags": tags,
        "type": type,
        "rating": {
            "amount": 0,
            "weight": 0,
            "value": 0
        }
    }

    with open("websiteFiles/data/parks.json",'r+') as file:
        fileData = json.load(file)
        fileData.append(newPark) # add park to parks.json data
        file.seek(0)
        json.dump(fileData, file, indent = 4) # turn back into JSON file

    # Save uploaded images
    imageFolder = os.path.join(app.static_folder,'data/photos')
    uploaded_files = request.files.getlist('uploadFile') # get uploaded photos from form
    for i, image in enumerate(uploaded_files): # go through all photos
        ext = os.path.splitext(image.filename)[1] # get the file name extension
        filename = f"{id}-{chr(97+i)}{ext}" # give the photos names like _-a.jpg, _-b.jpg, etc. where _ is the park id
        image.save(os.path.join(imageFolder, secure_filename(filename)))

    return redirect(f'/parkPage.html?id={id}')


if __name__ == '__main__':
    app.run(debug=True, port=3000)