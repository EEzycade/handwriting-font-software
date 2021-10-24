from app import app
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from werkzeug.utils import secure_filename
# Before submission, we should change this to only import the methods needed
from app.image_to_font_utils import *
import os
from cv2 import imwrite, imread

def allowed_image(filename):
    ''' Check that the file extension is an accepted image '''
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_IMAGE_EXTENSIONS']

def allowed_image_filesize(filesize):
    ''' Check that the file size is less than the allowed maximum '''
    return filesize < app.config['MAX_IMAGE_SIZE']

@app.route('/')
def index():
    return render_template('public/index.html', title='Home')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':

        # check if the post request has the file part
        if 'image' not in request.files:
            flash('No image in upload')
            return redirect(request.url)
        image = request.files['image']
        filename = secure_filename(image.filename)

        # if user does not select file, browser also
        # submit a empty part without filename
        if filename == '':
            flash('No selected image', 'warning')
            return redirect(request.url)
        
        if image and allowed_image(image.filename):
            image.seek(0, os.SEEK_END)
            size = image.tell()
            if allowed_image_filesize(size):
                os.makedirs(app.config['IMAGE_UPLOADS'], exist_ok=True)
                image.seek(0)
                image.save(os.path.join(app.config['IMAGE_UPLOADS'], filename))
                flash('Image uploaded successfully', 'success')
                return redirect(request.url)
            else:
                flash('Image size is too large', 'danger')
                return redirect(request.url)
        else:
            flash('Invalid file type', 'danger')
            return redirect(request.url)

    return render_template('public/upload.html', title='Upload')

@app.route('/image_to_font', methods=['GET', 'POST'])
def image_to_font():
    if request.method == 'POST':

        # check if the post request has the file part
        if 'image' not in request.files:
            flash('No image in upload')
            return redirect(request.url)
        image = request.files['image']

        # get the template type
        templateType = request.values['template_type']

        # if user does not select file, browser also
        # submit a empty part without filename
        if image.filename == '':
            flash('No selected image', 'warning')
            return redirect(request.url)
        
        if image and allowed_image(image.filename):
            image.seek(0, os.SEEK_END)
            size = image.tell()
            if allowed_image_filesize(size):
                image.seek(0, os.SEEK_END)
                size = image.tell()
                if allowed_image_filesize(size):
                
                # upload image
                    filename = secure_filename(image.filename)
                    os.makedirs(app.config['IMAGE_UPLOADS'], exist_ok=True)
                    os.makedirs(app.config['PROCESSED_IMAGES'], exist_ok=True)
                    upload_filepath = os.path.join(app.config['IMAGE_UPLOADS'], filename)
                    image.seek(0)
                    image.save(upload_filepath)
                    flash('Image uploaded successfully', 'success')

                    # process image
                    processedImage = process_image(imread(upload_filepath))
                    os.makedirs(app.config['PROCESSED_IMAGES'], exist_ok=True)
                    imwrite(os.path.join(app.config['PROCESSED_IMAGES'], filename),processedImage)
                    flash('Image processed successfully', 'success')

                    # cut image
                    symbols = template_symbols_dict[templateType]
                    cutImages = cut_image(processedImage, templateType)
                    cutImagePath = os.path.join(app.config['CUT_IMAGES'], image.filename)
                    os.makedirs(cutImagePath, exist_ok=True)
                    for symbol, cutImage in zip(symbols, cutImages):
                        imwrite(os.path.join(cutImagePath, symbol + ".jpg"),cutImage)
                    flash('Image cut successfully', 'success')

                    return redirect(request.url)
                else:
                    flash('Image size is too large', 'danger')
                    return redirect(request.url)
            else:
                flash('Invalid file type', 'danger')
                return redirect(request.url)

    return render_template('public/image_to_font.html', title='Image To Font')
