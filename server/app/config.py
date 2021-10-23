class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = "a84ckkPu1reWiMFURW7oaA"

    IMAGE_UPLOADS = "./app/uploads/"

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