from flask.helpers import send_from_directory
from app import app
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort, Response
from datetime import datetime
from werkzeug.utils import secure_filename
from app.utils.security import requires_auth, devEnvironment
from app.utils.security import requires_auth
from bmark.image import process_image, detect_gridlines, dev_grid_picture, cut_image, resize_image, unbox_image
from app.utils.web_utils import allowed_image, allowed_image_filesize, get_glyph, get_font_list
from app.utils.constants import template_symbols_dict
# from app.utils.font_generator import gen_font
from bmark import font
# from app.utils.alt.imagetotext import image_to_text
from bmark.ml import image_to_text
import os
from cv2 import imwrite, imread
from shutil import rmtree

@app.route('/', methods=['GET'])
@devEnvironment
def index():
    """
    Summary: Homepage in the dev backend testing environment.
    Author: Hans Husurianto
    """
    return render_template('public/image_to_font.html', title='Image To Font')

# Route to process an image
# Author: Hans Husurianto, Braeden Burgard
@app.route('/process', methods=['POST'])
@requires_auth
def process():
    """
    Summary: Endpoint for the API to process an image into a font.
    @param key: API Key in header for authentication
    @param image: Image in the body to be processed
    """
    # This route only accepts POST requests
    if request.method == 'POST':

        # Check for image in request and retrieve
        # Author: Hans Husurianto
        if 'image' not in request.files:
            flash('No image in upload', 'danger')
            return render_template('public/image_to_font.html', title='Image To Font')
        image = request.files['image']

        # Check that image has a filename
        # Author: Hans Husurianto
        if image.filename == '':
            flash('No selected image', 'warning')
            return render_template('public/image_to_font.html', title='Image To Font')

        # Retrieve Template Type
        # Authors: Braeden Burgard & Hans Husurianto
        if 'template_type' not in request.form:
            flash('No template type selected', 'danger')
            return render_template('public/image_to_font.html', title='Image To Font')
        elif request.form['template_type'] not in template_symbols_dict:
            flash('Invalid template type', 'warning')
            return render_template('public/image_to_font.html', title='Image To Font')
        template  = template_symbols_dict[request.values['template_type']]

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

                    # Process Image, clean image
                    # processed_image_tuple is a tuple (image,ratio)
                    # Author: Michaela Chen
                    processed_image_tuple = process_image(
                        imread(upload_filepath))
                    clean(app.config['PROCESSED_IMAGES'])
                    imwrite(os.path.join(
                        app.config['PROCESSED_IMAGES'], filename), processed_image_tuple[0])
                    flash('Image processed successfully', 'success')

                    # find grid lines. For dev use only, this part is only for debugging purposes
                    # Author: Braeden Burgard
                    resized_image = resize_image(processed_image_tuple[0], 200)[0]
                    processed_image = processed_image_tuple[0]
                    grid_positions_tuple = detect_gridlines(
                        resized_image, template)
                    grid_line_image = dev_grid_picture(
                        resized_image, grid_positions_tuple[0], grid_positions_tuple[1])
                    clean(app.config['GRID_IMAGES'])
                    imwrite(os.path.join(
                        app.config['GRID_IMAGES'], filename), grid_line_image)
                    flash('Grid line estimate processed successfully', 'success')

                    # cut image. cutImages is a tuple (cut_images, flattened_template)
                    cut_images_tuple = cut_image(
                        processed_image, resized_image, template, processed_image_tuple[1])
                    cut_image_path = os.path.join(
                        app.config['CUT_IMAGES'], image.filename)
                    unboxed_image_path = os.path.join(
                        app.config["UNBOXED_IMAGES"],
                        os.path.splitext(image.filename)[0]
                    )
                    clean(cut_image_path)
                    clean(unboxed_image_path)
                    for cutImage, symbol in zip(cut_images_tuple[0], cut_images_tuple[1]):
                        if symbol != None:
                            if cutImage.size == 0:
                                flash(
                                    "Grid estimation error, check output", "warning")
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
                    font.create(
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
        abort(400, "Invalid request. Please use POST.")
    
    # Check for image in request (body) and retrieve
    if 'image' not in request.files:
        flash('No image in upload', 'danger')
        abort(400, "No image in upload")
    
    # Get the image and image details
    image = request.files['image']
    filename = secure_filename(image.filename)
    fontname = os.path.splitext(filename)[0]

    # Check that the image has a filename
    if filename == '':
        flash('No selected image', 'warning')
        abort(400, "No selected image")

    # Retrieve Template Type
    # Authors: Braeden Burgard & Hans Husurianto
    templateType = "english_lower_case_letters"
    if 'template_type' in request.form and request.form['template_type'] not in template_symbols_dict:
        flash('Invalid template type', 'warning')
        abort(400, "Invalid template type: %s" % request.form['template_type'])
    elif 'template_type' in request.form:
        templateType = request.form['template_type']

    # Check that the image has an appropriate name
    # Author: Hans Husurianto
    if not allowed_image(filename):
        flash('Invalid image type', 'warning')
        abort(400, "Invalid image type: %s" % filename)
    
    # Check that the image is smaller than the maximum allowed size
    # Author: Hans Husurianto
    image.seek(0, os.SEEK_END)
    size = image.tell()
    if not allowed_image_filesize(size):
        flash('Image too large', 'warning')
        abort(400, "Image too large: %s" % filename)
    
    # Upload Image
    clean(app.config['IMAGE_UPLOADS']) # Clean up old images
    clean(app.config['PROCESSED_IMAGES']) # Clean up old images
    upload_filepath = os.path.join(
        app.config['IMAGE_UPLOADS'], filename) # Get upload filepath
    image.seek(0) # Reset file pointer
    image.save(upload_filepath) # Save image to filepath
    flash('Image uploaded successfully', 'success')

    # Process Image, clean image
    # processed_image_tuple is a tuple (image,ratio)
    # Author: Michaela Chen
    processed_image_tuple = process_image(imread(upload_filepath)) 
    clean(app.config['PROCESSED_IMAGES'])
    imwrite(os.path.join(
        app.config['PROCESSED_IMAGES'], filename), processed_image_tuple[0])
    flash('Image processed successfully', 'success')

    # Find grid lines. For dev use only, this part is only for debugging purposes
    # Author: Braeden Burgard
    if app.config["DEBUG"]:
        resized_image = resize_image(processed_image_tuple[0], 200)[0]
        processed_image = processed_image_tuple[0]
        grid_positions_tuple = detect_gridlines(
            resized_image, templateType)
        grid_line_image = dev_grid_picture(
            resized_image, grid_positions_tuple[0], grid_positions_tuple[1])
        clean(app.config['GRID_IMAGES'])
        imwrite(os.path.join(
            app.config['GRID_IMAGES'], filename), grid_line_image)
        flash('Grid line estimate processed successfully', 'success')

    # Cut image. cutImages is a tuple (cut_images, flattened_template)
    # cut_images_tuple = cut_image(imread(upload_filepath), processed_image, templateType, processed_image_tuple[1])
    cut_images_tuple = cut_image(
        processed_image, resized_image, templateType, processed_image_tuple[1])
    cut_image_path = os.path.join(
        app.config['CUT_IMAGES'], filename)
    unboxed_image_path = os.path.join(
        app.config["UNBOXED_IMAGES"],
        fontname
    )
    clean(cut_image_path)
    clean(unboxed_image_path)
    for cutImage, symbol in zip(cut_images_tuple[0], cut_images_tuple[1]):
        if symbol != None:
            if cutImage.size == 0:
                flash("Grid estimation error, check output", "warning")
            else:
                imwrite(os.path.join(cut_image_path, symbol + ".jpg"), cutImage)
                imwrite(os.path.join(unboxed_image_path, symbol + ".jpg"), unbox_image(cutImage))
    flash('Image cut successfully', 'success')

    # Convert cut images into svgs
    # Author: Andrew Bauer
    # Convert SVGs into a font
    # Author: Andrew Silkwood
    svg_path = os.path.join(app.config['SVG_IMAGES'], fontname)
    clean(svg_path)
    gen_font(
            unboxed_image_path,
            svg_path,
            os.path.join(
                app.config['FONTS_FOLDER2'],
                fontname + ".otf"
            )
    )

    return Response("{'message':'Successfully converted image to font','filename':'"+ fontname + ".otf" +"'}", status=201)

@app.route('/identify_character', methods=['POST'])
@requires_auth
def identify_character():
    """
    Description: Endpoint for the API to identify a character in an image.
    Author: Hans Husurianto, Raghav Bansal for image_to_text

    @param key: API Key in header for authentication
    @param image: Image in the body to be identified
    """
    if request.method != 'POST':
        abort(400, "Invalid request. Please use POST.")
    
    # Check if the post request has an image
    if 'image' not in request.files:
        abort(400, "No image in upload")

    # Get the image and image details
    image = request.files['image']
    filename = secure_filename(image.filename)

    # Check that the image has a filename
    if filename == '':
        abort(400, "No selected image")

    # Check that the image has an appropriate name
    if not allowed_image(filename):
        abort(400, "Invalid image type: %s" % filename)
    
    # Check that the image is smaller than the maximum allowed size
    image.seek(0, os.SEEK_END)
    size = image.tell()
    if not allowed_image_filesize(size):
        abort(400, "Image too large: %s" % filename)
    
    # Upload Image
    filename = secure_filename(image.filename)
    clean(app.config['IMAGE_UPLOADS'])
    clean(app.config['PROCESSED_IMAGES'])
    upload_filepath = os.path.join(
        app.config['IMAGE_UPLOADS'], filename)
    image.seek(0)
    image.save(upload_filepath)

    # Identify character
    text = image_to_text(upload_filepath)
    return Response("{'message':'Successfully identified character','character':'"+ text +"'}", status=200)

@app.route('/font/<path:filename>')
@requires_auth
def font(filename):
    """
    Description: Endpoint for the API to serve a font file.
    Author: Hans Husurianto

    @param filename: File name of a font on the server, extension assumes .otf if not provided
    @return: Font file
    """
    extension = os.path.splitext(filename)[1]
    if not extension in ['.otf', '.ttf']:
        filename += '.otf'
    return send_from_directory(app.config['FONTS_FOLDER'], secure_filename(filename), as_attachment=True)

@app.route('/preview')
@devEnvironment
def preview():
    """
    Description: Page for previewing the font. Only accessible on the dev environment.
    Author: Hans Husurianto
    """
    if request.args and request.args['font'] and request.args['font'] in get_font_list():
        return render_template('public/preview.html', title='Font Preview', args=request.args['font'])

    for f in request.args.items():
        if f[0] in get_font_list():
            return render_template('public/preview.html', title='Font Preview', args=f[0])
    return render_template('public/preview.html', title='Font Preview', args='AmogusFont.ttf')

def clean(path):
    """
    Description: Deletes all files in a directory.
    Author: Andrew Bauer

    @param path: Path to the directory to be cleaned
    """
    try:
        rmtree(path)
        print(f"Cleared '{path}'")
    except FileNotFoundError:
        pass
    os.makedirs(path, exist_ok=True)
