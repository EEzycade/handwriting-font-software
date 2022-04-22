class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = "a84ckkPu1reWiMFURW7oaA"
    API_KEY = "254edfd6687a17117e5cfabe6e190cfa"
    IP = "127.0.0.1"

    IMAGE_UPLOADS = "./app/uploads/"
    PROCESSED_IMAGES = "./app/processed_images"
    GRID_IMAGES = "./app/grid_estimate_images"
    CUT_IMAGES = "./app/cut_images"
    UNBOXED_IMAGES = "./app/unboxed_images"
    SVG_IMAGES = "./app/svgs"
    FONTS_FOLDER = "./fonts"
    FONTS_FOLDER2 = "./app/fonts"
    FONTS_FOLDER3 = "./app/base_fonts"
    TEMPLATES_FOLDER = "./app/character-templates"
    TEMPLATE_IMAGES_FOLDER = "./template_images"

    DEFAULT_BASE_FONT = "ComicSans.ttf"

    ALLOWED_IMAGE_EXTENSIONS = ["png", "jpg", "jpeg"]
    MAX_IMAGE_SIZE = 8 * 1024 * 1024  # 8MB

    SESSION_COOKIE_SECURE = True

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_STORE = False

class TestingConfig(Config):
    TESTING = True
    SESSION_COOKIE_STORE = False