Getting Started
===============

.. _prerequisites:

Pre-requisites
--------------

Make sure you have the following pre-requisites:

* `Git <http://git-scm.com/>`_ 
* `Python 3.9 or newer <https://docs.python.org/3>`_

Installation
------------

.. dropdown:: Windows Installation

    To install BookMarked Handwriting Software on Windows,
    first clone the repository:

    .. code-block:: console

        $ git clone https://github.com/EEzycade/handwriting-font-software.git

    Navigate to the server app directory:

    .. code-block:: console

        $ cd handwriting-font-software/server/app

    Set up the environment:

    .. code-block:: console

        $ python -m venv env
        $ .\env\Scripts\activate

    Then install the dependencies:

    .. code-block:: console

        (env) $ pip install -r requirements.txt

.. dropdown:: Linux Installation

    To install BookMarked Handwriting Software on Linux,
    first clone the repository:

    .. code-block:: console

        $ git clone https://github.com/EEzycade/handwriting-font-software.git

    Navigate to the server app directory:

    .. code-block:: console

        $ cd handwriting-font-software/server/app

    Set up the environment:

    .. code-block:: console

        $ python -m venv env
        $ source ./env/bin/activate

    Install dependencies:

    .. code-block:: console

        (env) $ pip install -r requirements.txt

Running the Flask API Server
-----------------------------

To run the Flask API Server, run the following command:

.. code-block:: console

    $ .\env\Scripts\activate
    (env) $ flask run

Configuration
-------------

Under the ``.flaskenv`` file,
you may find server settings to configure:

.. code-block::

    #.flaskenv
    FLASK_APP=app
    FLASK_ENV=development

``FLASK_APP``
    The name of the application script to run. We use "app".

``FLASK_ENV``
    The environment in which we are running the application.
    Valid environment settings include: ``development``
    and ``production``. Environment settings can be configured under
    :doc:`config`.