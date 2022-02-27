from flask.helpers import send_from_directory
from app import app
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from werkzeug.utils import secure_filename
from app.utils.security import requires_auth
from app.utils.photo_manipulation_utils import process_image, detect_gridlines, dev_grid_picture, cut_image, resize_image
from app.utils.web_utils import allowed_image, allowed_image_filesize, get_glyph, get_font_list
from app.utils.constants import template_symbols_dict
import os
from cv2 import imwrite, imread

# Home Page
@app.route('/', methods=['GET'])
def index():
    return render_template('public/image_to_font.html', title='Image To Font')

# Route to process an image
@app.route('/process', methods=['POST'])
#@requires_auth
def process():
    # This route only accepts POST requests
    if request.method == 'POST':

        # Check for image in request and retrieve
        # Author: Hans Husurianto
        if 'image' not in request.files:
            flash('No image in upload', 'danger')
            return render_template('public/image_to_font.html', title='Image To Font')
        image = request.files['image']

        # Retrieve Template Type
        # Authors: Braeden Burgard & Hans Husurianto
        if 'template_type' not in request.form:
            flash('No template type selected', 'danger')
            return render_template('public/image_to_font.html', title='Image To Font')
        elif request.form['template_type'] not in template_symbols_dict:
            flash('Invalid template type', 'warning')
            return render_template('public/image_to_font.html', title='Image To Font')
        templateType = request.values['template_type']

        # Check that image has a filename
        # Author: Hans Husurianto
        if image.filename == '':
            flash('No selected image', 'warning')
            return render_template('public/image_to_font.html', title='Image To Font')
        
        
        if image and allowed_image(image.filename):
            image.seek(0, os.SEEK_END)
            size = image.tell()
            if allowed_image_filesize(size):
                image.seek(0, os.SEEK_END)
                size = image.tell()
                if allowed_image_filesize(size):
                
                    # Upload Image
                    filename = secure_filename(image.filename)
                    os.makedirs(app.config['IMAGE_UPLOADS'], exist_ok=True)
                    os.makedirs(app.config['PROCESSED_IMAGES'], exist_ok=True)
                    upload_filepath = os.path.join(app.config['IMAGE_UPLOADS'], filename)
                    image.seek(0)
                    image.save(upload_filepath)
                    flash('Image uploaded successfully', 'success')

                    # Process Image, clean image
                    # processed_image_tuple is a tuple (image,ratio)
                    # Author: Michaela Chen
                    processed_image_tuple = process_image(imread(upload_filepath))
                    os.makedirs(app.config['PROCESSED_IMAGES'], exist_ok=True)
                    imwrite(os.path.join(app.config['PROCESSED_IMAGES'], filename),processed_image_tuple[0])
                    flash('Image processed successfully', 'success')

                    # find grid lines. For dev use only, this part is only for debugging purposes
                    # Author: Braeden Burgard
                    resized_image = resize_image(processed_image_tuple[0], 200)[0]
                    processed_image = processed_image_tuple[0]
                    grid_positions_tuple = detect_gridlines(resized_image, templateType)
                    grid_line_image = dev_grid_picture(resized_image, grid_positions_tuple[0], grid_positions_tuple[1])
                    os.makedirs(app.config['GRID_IMAGES'], exist_ok=True)
                    imwrite(os.path.join(app.config['GRID_IMAGES'], filename),grid_line_image)
                    flash('Grid line estimate processed successfully', 'success')

                    # cut image. cutImages is a tuple (cut_images, flattened_template)
                    #cut_images_tuple = cut_image(imread(upload_filepath), processed_image, templateType, processed_image_tuple[1])
                    cut_images_tuple = cut_image(processed_image, resized_image, templateType, processed_image_tuple[1])
                    cut_image_path = os.path.join(app.config['CUT_IMAGES'], image.filename)
                    os.makedirs(cut_image_path, exist_ok=True)
                    for cutImage, symbol in zip(cut_images_tuple[0], cut_images_tuple[1]):
                        if symbol != None:
                            if cutImage == []:
                                flash("Grid estimation error, check output", "warning")
                            else:
                                imwrite(os.path.join(cut_image_path, symbol + ".jpg"),cutImage)
                    flash('Image cut successfully', 'success')

                    # Andrew Bauer's code
                    # TODO: convert to svg format (which should include processing)
                    # TODO: turn into font

                    return render_template('public/image_to_font.html', title='Image To Font')
                else:
                    flash('Image size is too large', 'warning')
                    return render_template('public/image_to_font.html', title='Image To Font')
            else:
                flash('Invalid file type', 'warning')
                return render_template('public/image_to_font.html', title='Image To Font')
    else:
        flash('Invalid request', 'danger')
        return render_template('public/image_to_font.html', title='Image To Font')

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

@app.route('/fonts/<path:filename>')
def fonts(filename):
    return send_from_directory(app.config['FONTS_FOLDER'], secure_filename(filename), as_attachment=True)

@app.route('/preview')
def preview():
    if request.args:
        if request.args['font']:
            data = request.args['font']
            if data in get_font_list():
                return render_template('public/preview.html', title='Font Preview', args=data)
    for f in request.args.items():
        if f[0] in get_font_list():
            return render_template('public/preview.html', title='Font Preview', args=f[0])    
    return render_template('public/preview.html', title='Font Preview', args='AmogusFont.ttf')