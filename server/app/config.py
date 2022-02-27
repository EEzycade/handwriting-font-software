class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = "a84ckkPu1reWiMFURW7oaA"
    API_KEY = "254edfd6687a17117e5cfabe6e190cfa"

    IMAGE_UPLOADS = "./app/uploads/"
    PROCESSED_IMAGES = "./app/processed_images"
    GRID_IMAGES = "./app/grid_estimate_images"
    CUT_IMAGES = "./app/cut_images"
    FONTS_FOLDER = "./fonts"

    ALLOWED_IMAGE_EXTENSIONS = ["png", "jpg", "jpeg"]
    MAX_IMAGE_SIZE = 8 * 1024 * 1024 # 8MB
    
    SESSION_COOKIE_SECURE = True

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True

    SESSION_COOKIE_STORE = False

class TestingConfig(Config):
    TESTING = True

    SESSION_COOKIE_STORE = False