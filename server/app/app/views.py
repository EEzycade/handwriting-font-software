from flask.helpers import send_from_directory
from app import app
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from werkzeug.utils import secure_filename
# Before submission, we should change this to only import the methods needed
from app.utils.photo_manipulation_utils import *
import os
from cv2 import imwrite, imread

glyphs = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '=', '+', '{', '[', '}', ']', '|', ':', ';', '"', '\'', '<', ',', '>', '.', '?', '/', '\\', '~', '`'
]

def allowed_image(filename):
    ''' Check that the file extension is an accepted image '''
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_IMAGE_EXTENSIONS']

def allowed_image_filesize(filesize):
    ''' Check that the file size is less than the allowed maximum '''
    return filesize < app.config['MAX_IMAGE_SIZE']

def get_glyph(idx):
    ''' Get the glyph from the glyphs list '''
    if(idx < len(glyphs)):
        return glyphs[idx]
    else:
        return ''
app.jinja_env.globals.update(get_glyph=get_glyph)

def get_font_list():
    ''' Get the list of fonts from the fonts folder '''
    return os.listdir('./app/' + app.config['FONTS_FOLDER'])
app.jinja_env.globals.update(get_font_list=get_font_list)

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

                    # process image. processedImage is a tuple (image,ratio)
                    processed_image_tuple = process_image(imread(upload_filepath))
                    os.makedirs(app.config['PROCESSED_IMAGES'], exist_ok=True)
                    imwrite(os.path.join(app.config['PROCESSED_IMAGES'], filename),processed_image_tuple[0])
                    flash('Image processed successfully', 'success')

                    # find grid lines. For dev use only, this part is only for debugging purposes
                    grid_positions_tuple = detect_gridlines(processed_image_tuple[0], templateType)
                    grid_line_image = dev_grid_picture(processed_image_tuple[0], grid_positions_tuple[0], grid_positions_tuple[1])
                    os.makedirs(app.config['GRID_IMAGES'], exist_ok=True)
                    imwrite(os.path.join(app.config['GRID_IMAGES'], filename),grid_line_image)
                    flash('Grid line estimate processed successfully', 'success')

                    # cut image. cutImages is a tuple (cut_images, flattened_template)
                    cut_images_tuple = cut_image(imread(upload_filepath), processed_image_tuple[0], templateType, processed_image_tuple[1])
                    cut_image_path = os.path.join(app.config['CUT_IMAGES'], image.filename)
                    os.makedirs(cut_image_path, exist_ok=True)
                    for cutImage, symbol in zip(cut_images_tuple[0], cut_images_tuple[1]):
                        if symbol != None:
                            if cutImage == []:
                                flash("Grid estimation error, check output", "warning")
                            else:
                                imwrite(os.path.join(cut_image_path, symbol + ".jpg"),cutImage)
                    flash('Image cut successfully', 'success')

                    return redirect(request.url)
                else:
                    flash('Image size is too large', 'danger')
                    return redirect(request.url)
            else:
                flash('Invalid file type', 'danger')
                return redirect(request.url)

    return render_template('public/image_to_font.html', title='Image To Font')

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