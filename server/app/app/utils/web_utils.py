import os
from app import app
from app.utils.constants import glyphs

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