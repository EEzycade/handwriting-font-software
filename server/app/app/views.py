from app import app
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from werkzeug.utils import secure_filename
import os

def allowed_image(filename):
    ''' Check that the file extension is an accepted image '''
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_IMAGE_EXTENSIONS']

def allowed_image_filesize(filesize):
    ''' Check that the file size is less than the allowed maximum '''
    return filesize < app.config['MAX_IMAGE_SIZE']

@app.route("/")
def index():
    return render_template("public/index.html", title="Home")

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':

        # check if the post request has the file part
        if 'image' not in request.files:
            flash('No image in upload')
            return redirect(request.url)
        image = request.files['image']

        # if user does not select file, browser also
        # submit a empty part without filename
        if image.filename == '':
            flash('No selected image', 'warning')
            return redirect(request.url)
        
        if image and allowed_image(image.filename):
            if allowed_image_filesize(len(image.read())):
                filename = secure_filename(image.filename)
                os.makedirs(app.config['IMAGE_UPLOADS'], exist_ok=True)
                image.save(os.path.join(app.config['IMAGE_UPLOADS'], filename))
                flash('Image uploaded successfully', 'success')
                return redirect(request.url)
            else:
                flash('Image size is too large', 'danger')
                return redirect(request.url)
        else:
            flash('Invalid file type', 'danger')
            return redirect(request.url)

    return render_template("public/upload.html", title="Upload")
