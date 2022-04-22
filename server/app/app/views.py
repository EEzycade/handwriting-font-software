from flask.helpers import send_from_directory
from app import app
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort, Response
from datetime import datetime
from werkzeug.utils import secure_filename
from app.utils.security import requires_auth, devEnvironment
from app.utils.web_utils import allowed_image, allowed_image_filesize, get_glyph, get_font_list
from app.utils import web_utils
import os
from cv2 import imwrite, imread
from shutil import rmtree
import bmark

@app.route('/', methods=['GET'])
@devEnvironment
def index():
    """
    Summary: Homepage in the dev backend testing environment.
    Author: Hans Husurianto
    """
    return render_template('public/image_to_font.html',
                           title='Image To Font',
                           base_fonts=web_utils.base_font_list(),
                           templates=web_utils.template_dict(),
    )

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

    if request.method != 'POST':
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
    templateType = secure_filename(request.form.get('template_type', "english_lower_case_letters"))
    if templateType not in web_utils.template_dict():
        flash('Invalid template type', 'warning')
        abort(400, "Invalid template type: %s" % templateType)
    template = web_utils.load_template(templateType)

    # Retrieve Base Font
    # Author: Andrew Bauer
    base_font = secure_filename(
            request.form.get("base_font", app.config['DEFAULT_BASE_FONT'])
    )
    if os.path.exists(os.path.join(app.config["FONTS_FOLDER3"], base_font)):
        print(f"Using '{base_font}' for missing characters.")
    else:
        flash(f'The base font \'{request.form["base_font"]}\' does not exist. Using the default base font \'{base_font}\' instead.', 'warning')
        print(f'The base font \'{request.form["base_font"]}\' does not exist. Using the default base font \'{base_font}\' instead.')
        base_font = app.config['DEFAULT_BASE_FONT']

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
    processed_image_tuple = bmark.image.process(imread(upload_filepath))
    clean(app.config['PROCESSED_IMAGES'])
    imwrite(os.path.join(
        app.config['PROCESSED_IMAGES'], filename), processed_image_tuple[0])
    flash('Image processed successfully', 'success')

    # Find grid lines. For dev use only, this part is only for debugging purposes
    # Author: Braeden Burgard
    if app.config["DEBUG"]:
        resized_image = bmark.image.resize(processed_image_tuple[0], 200)[0]
        processed_image = processed_image_tuple[0]
        grid_positions_tuple = bmark.image.detect_gridlines(
            resized_image, template)
        grid_line_image = bmark.image.dev_grid_picture(
            resized_image, grid_positions_tuple[0], grid_positions_tuple[1])
        clean(app.config['GRID_IMAGES'])
        imwrite(os.path.join(
            app.config['GRID_IMAGES'], filename), grid_line_image)
        flash('Grid line estimate processed successfully', 'success')

    # Cut image. cutImages is a tuple (cut_images, flattened_template)
    # cut_images_tuple = cut_image(imread(upload_filepath), processed_image, templateType, processed_image_tuple[1])
    cut_images_tuple = bmark.image.cut(
        processed_image, resized_image, template, processed_image_tuple[1])
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
                imwrite(os.path.join(unboxed_image_path, symbol + ".jpg"), bmark.image.unbox(cutImage))
    flash('Image cut successfully', 'success')

    # Convert cut images into svgs
    # Author: Andrew Bauer
    # Convert SVGs into a font
    # Author: Andrew Silkwood
    svg_path = os.path.join(app.config['SVG_IMAGES'], fontname)
    font_path = os.path.join(app.config['FONTS_FOLDER2'], fontname + ".otf")
    clean(svg_path)
    bmark.font.create(unboxed_image_path, svg_path, font_path)

    # Pull missing characters from a base font
    # Author: Andrew Bauer
    base_font_path = os.path.join(app.config['FONTS_FOLDER3'], base_font)
    assert os.path.exists(base_font_path)
    bmark.font.merge_font(font_path, base_font_path, output_file=font_path)

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
    text = bmark.ml.image_to_text(upload_filepath)
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

@app.route('/base-fonts', methods=['GET'])
def base_font_list():
    return jsonify(web_utils.base_font_list())

@app.route('/templates', methods=['GET'])
def template_dict():
    return jsonify(web_utils.template_dict())

@app.route('/render-template/<path:template_name>')
def create_template(template_name):
    template_name = secure_filename(template_name)
    if not os.path.exists(os.path.join(app.config["TEMPLATES_FOLDER"], template_name)):
        print(f"Template '{template_name}' not found.")
        abort(400, f"Template '{template_name}' not found.")
    template = web_utils.load_template(template_name)
    height = len(template)
    width = len(template[0]) if template else 0
    image = bmark.template.create(width*height, 50, 5)
    image.save(os.path.join("app", app.config["TEMPLATE_IMAGES_FOLDER"], template_name + ".png"))
    return send_from_directory(app.config["TEMPLATE_IMAGES_FOLDER"], template_name + ".png", as_attachment=True)

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
