from flask.helpers import send_from_directory
from app import app
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from werkzeug.utils import secure_filename
from app.utils.security import requires_auth
from app.utils.photo_manipulation_utils import process_image, detect_gridlines, dev_grid_picture, cut_image, resize_image, unbox_image, crop
from app.utils.web_utils import allowed_image, allowed_image_filesize, get_glyph, get_font_list
from app.utils.constants import template_symbols_dict
from app.utils.font_generator import gen_font
import os
from cv2 import imwrite, imread
from shutil import rmtree

# Home Page


@app.route('/', methods=['GET'])
def index():
    return render_template('public/image_to_font.html', title='Image To Font')

# Route to process an image


@app.route('/process', methods=['POST'])
# @requires_auth
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
        template_type = request.values['template_type']
        template = template_symbols_dict[template_type]

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
                    clean(app.config['IMAGE_UPLOADS'])
                    clean(app.config['PROCESSED_IMAGES'])
                    upload_filepath = os.path.join(
                        app.config['IMAGE_UPLOADS'], filename)
                    image.seek(0)
                    image.save(upload_filepath)
                    flash('Image uploaded successfully', 'success')

                     # Upload Image
                    clean(app.config['IMAGE_UPLOADS']) # Clean up old images
                    clean(app.config['PROCESSED_IMAGES']) # Clean up old images
                    upload_filepath = os.path.join(
                        app.config['IMAGE_UPLOADS'], filename) # Get upload filepath
                    image.seek(0) # Reset file pointer
                    image.save(upload_filepath) # Save image to filepath
                    flash('Image uploaded successfully', 'success')

                    # Process Image, clean image
                    # Author: Michaela Chen, Braeden Burgard
                    cropped_image = crop(imread(upload_filepath))
                    clean(app.config['CROPPED_IMAGES'])
                    imwrite(os.path.join(
                        app.config['CROPPED_IMAGES'], filename), cropped_image)
                    processed_image = process_image(cropped_image, 500) 
                    clean(app.config['PROCESSED_IMAGES'])
                    imwrite(os.path.join(
                        app.config['PROCESSED_IMAGES'], filename), processed_image)
                    flash('Image processed successfully', 'success')

                    # Find grid lines. For dev use only, this part is only for debugging purposes
                    # Author: Braeden Burgard
                    if app.config["DEBUG"]:
                        [horizontal_lines, vertical_lines, score] = detect_gridlines(
                            processed_image, template)
                        print("***** Gridline score: ", score, " *****")
                        grid_line_image = dev_grid_picture(
                            processed_image, horizontal_lines, vertical_lines)
                        clean(app.config['GRID_IMAGES'])
                        imwrite(os.path.join(
                            app.config['GRID_IMAGES'], filename), grid_line_image)
                        flash('Grid line estimate processed successfully', 'success')

                    # Cut image. cutImages is a tuple (cut_images, flattened_template)
                    cuttable_image = process_image(cropped_image, 1500) 
                    [cut_images, flattened_template] = cut_image(
                        cuttable_image, processed_image, template)
                    cut_image_path = os.path.join(
                        app.config['CUT_IMAGES'], filename)
                    unboxed_image_path = os.path.join(
                        app.config["UNBOXED_IMAGES"],
                        filename
                    )
                    clean(cut_image_path)
                    clean(unboxed_image_path)
                    for cutImage, symbol in zip(cut_images, flattened_template):
                        if symbol != None:
                            if cutImage.size == 0:
                                flash("Grid estimation error, check output", "warning")
                            else:
                                imwrite(os.path.join(cut_image_path, symbol + ".jpg"), cutImage)
                                imwrite(os.path.join(unboxed_image_path, symbol + ".jpg"), unbox_image(cutImage))
                    flash('Image cut successfully', 'success')

                    # Convert cut images into svgs
                    # Author: Andrew Bauer
                    # Convert svgs into a font
                    # Author: Andrew Silkwood
                    svg_path = os.path.join(app.config['SVG_IMAGES'], os.path.splitext(image.filename)[0])
                    clean(svg_path)
                    gen_font(
                            unboxed_image_path,
                            svg_path,
                            os.path.join(
                                app.config['FONTS_FOLDER2'],
                                os.path.splitext(image.filename)[0] + ".otf"
                            )
                    )

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


@ app.route('/upload', methods=['GET', 'POST'])
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
                os.makedirs(app.config['IMAGE_UPLOADS'])
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


@ app.route('/fonts/<path:filename>')
def fonts(filename):
    return send_from_directory(app.config['FONTS_FOLDER'], secure_filename(filename), as_attachment=True)


@ app.route('/preview')
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

def clean(path):
    if app.config["DEBUG"]:
        try:
            rmtree(path)
            print(f"Cleared '{path}'")
        except FileNotFoundError:
            pass
    os.makedirs(path, exist_ok=True)
