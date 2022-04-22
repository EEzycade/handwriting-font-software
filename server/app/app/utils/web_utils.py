import os
from app import app
from app.utils.constants import glyphs

def allowed_image(filename):
    """
    Description: Check that the file extension is an accepted image
    Author: Hans Husurianto

    @param filename: filename to check
    @return: boolean
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_IMAGE_EXTENSIONS']

def allowed_image_filesize(filesize):
    """
    Description: Check that the file size is less than the allowed maximum
    Author: Hans Husurianto

    @param filesize: file size to check
    """
    return filesize < app.config['MAX_IMAGE_SIZE']

def get_glyph(idx):
    """
    Description: Get the glyph from the glyphs list
    Author: Hans Husurianto

    @param idx: index of the glyph
    @return: glyph
    """
    if(idx < len(glyphs)):
        return glyphs[idx]
    else:
        return ''
app.jinja_env.globals.update(get_glyph=get_glyph)

def get_font_list():
    """
    Description: Get the list of fonts from the fonts folder
    Author: Hans Husurianto
    
    @return: list of fonts
    """
    return os.listdir('./app/' + app.config['FONTS_FOLDER'])
app.jinja_env.globals.update(get_font_list=get_font_list)

def base_font_list() -> list[str]:
    """
    Description: List available base fonts
    Author: Andrew Bauer

    @return: List of the font names available
    """
    return os.listdir(app.config["FONTS_FOLDER3"])

