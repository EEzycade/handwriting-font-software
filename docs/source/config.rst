config.py
===================

API Configuration can be set in: ``server/app/config.py``

.. note:: 
    It is recommended to use the default values besides
    ``SECRET_KEY``, ``API_KEY`` and ``IP``.

.. currentmodule:: config

.. class:: Config

    Default configuration. ``SECRET_KEY``, ``API_KEY``, and ``IP``
    should not be changed here.
    It should be changed in :any:`ProductionConfig`.

    .. code-block:: python

        DEBUG = False
        TESTING = False
        SECRET_KEY = ""
        API_KEY = ""
        IP = "127.0.0.1"

        IMAGE_UPLOADS = "./app/uploads/"
        PROCESSED_IMAGES = "./app/processed_images"
        GRID_IMAGES = "./app/grid_estimate_images"
        CROPPED_IMAGES = "./app/cropped_images"
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

    ``DEBUG`` is set to ``True`` for development and ``False`` for production.
    
    ``TESTING`` is set to ``True`` for testing and ``False`` for production.

    ``SECRET_KEY`` is used for signing cookies.

    ``API_KEY`` is used for API authentication.

    ``IP`` is used for API authentication, from the frontend application.

    ``IMAGE_UPLOADS`` is the location of uploaded images.

    ``PROCESSED_IMAGES`` is the location of processed images.

    ``GRID_IMAGES`` is the location of images containing grid estimations.

    ``CROPPED_IMAGES`` is the location of cropped images (individual letters).

    ``UNBOXED_IMAGES`` is the location of cropped images without boxes.

    ``SVG_IMAGES`` is the location of SVGs converted from ``UNBOXED_IMAGES``.

    ``FONTS_FOLDER`` stores the location of fonts used for previewing.

    ``FONTS_FOLDER2`` is the location of processed fonts.

    ``FONTS_FOLDER3`` is the location of base fonts for missing characters.

    ``TEMPLATES_FOLDER`` is used for templating in generating fonts.

    ``TEMPLATE_IMAGES_FOLDER`` contains template images.

    ``DEFAULT_BASE_FONT`` is the default base font used for missing characters.

    ``ALLOWED_IMAGE_EXTENSIONS`` is the list of allowed image extensions.

    ``MAX_IMAGE_SIZE`` is the maximum size of an image.

    ``SESSION_COOKIE_SECURE`` is a ``boolean`` for whether session cookies
    are saved.
    
.. class:: ProductionConfig

    Production configuration.

    Internal ``SECRET_KEY``, ``API_KEY`` for authentication,
    and ``IP`` incoming should be set here.

    .. code-block:: python

        DEBUG = False
        TESTING = False
        SECRET_KEY = ""
        API_KEY = ""
        IP = "
    
.. class:: DevelopmentConfig

    Development configuration. Turns on DEBUG mode. The
    ``IP`` is set to local, ``127.0.0.1``.

.. class:: TestingConfig

    Testing configuration. Turns on TESTING mode.
    Currently minimally used for testing the API.