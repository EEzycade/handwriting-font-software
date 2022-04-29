API Reference
=============

.. tip:: 
    
    The code for the API can be found in ``server/app/app/views.py``.

Process Handwriting
-------------------------

:bdg-primary:`POST` /process

Main endpoint for processing handwriting into a font. This will NOT
return a font. The font must be subsequently called with the ``/font/<font_name>``
endpoint.

**Authorization** ``API Key in Header``

.. list-table::
    :header-rows: 1
    :align: left

    * - Key
      - Value
      - Requirement
    * - key
      - <value>
      - :code:`Required`

**Body** ``form-data``

.. list-table::
    :header-rows: 1
    :align: left

    * - Key
      - Value
      - Requirement
    * - image
      - image_file
      - :code:`Required`
    * - template_type
      - <template_type>
      - :code:`Optional`

``key`` is the API key set in the :doc:`config`, be sure to
specify the key in the header of the request.

``image`` is the submitted image from the user.

``template_type`` is the type of template to be used. Valid templates include:

* :code:`english_upper_case_letters`: English Uppercase Letters
* :code:`english_lower_case_letters`: English Lowercase Letters
* :code:`custom.csv`: Custom
* :code:`english_upperlower.csv`: English Letters Uppercase and Lowercase
* :code:`english_upper_lower_numbers.csv`: Numbers and English Letters (Uppercase and Lowercase)

**Response** ``JSON``

.. code-block:: JSON

    {
        "status": "status",
        "filename": "filename.otf"
    }

``status`` is the status of the request. It is recommended to use
the statusCode in the response and not the status.

``filename`` is the name of the file that was created.

.. dropdown:: Example Usage
    :color: secondary
    :icon: code

    .. tab-set::

        .. tab-item:: cURL
            :sync: key1

            .. code-block:: bash
                :linenos:

                curl --location --request POST 'http://{hostname}:5000/process' \
                --header 'key: SuperSecretAPIKey' \
                --form 'image=@"C:/Users/BookMarked/Downloads/TotallyRealImage.jpg"' \
                --form 'template_type="english_lower_case_letters"'

        .. tab-item:: Node.JS
            :sync: key2

            .. code-block:: javascript
                :linenos:

                var request = require('request');
                var fs = require('fs');
                var options = {
                    'method': 'POST',
                    'url': 'http://{hostname}:5000/process',
                    'headers': {
                        'key': 'SuperSecretAPIKey'
                    },
                    formData: {
                        'image': {
                            'value': fs.createReadStream('/C:/Users/BookMarked/Downloads/TotallyRealImage.jpg'),
                            'options': {
                                'filename': '/C:/Users/BookMarked/Downloads/TotallyRealImage.jpg',
                                'contentType': null
                            }
                        },
                        'template_type': 'english_lower_case_letters'
                    }
                };
                request(options, function (error, response) {
                    if (error) throw new Error(error);
                    console.log(response.body);
                });

        .. tab-item:: Python
            :sync: key3

            .. code-block:: python
                :linenos:

                import requests

                url = "http://{hostname}:5000/process"

                payload={'template_type': 'english_lower_case_letters'}
                files=[
                    ('image',('IMG_2638.jpg',open('/C:/Users/BookMarked/Downloads/TotallyRealImage.jpg','rb'),'image/jpeg'))
                ]
                headers = {
                    'key': 'SuperSecretAPIKey'
                }

                response = requests.request("POST", url, headers=headers, data=payload, files=files)

                print(response.text)

Retrieve Font
-------------------------

:bdg-primary:`GET` /font/<font_name>

**Authorization** ``API Key in Header``

.. list-table::
    :header-rows: 1
    :align: left

    * - Key
      - Value
      - Requirement
    * - key
      - <value>
      - :code:`Required`

``key`` is the API key set in the :doc:`config`, be sure to
specify the key in the header of the request.

``font_name`` is the name of the font to be retrieved.

.. dropdown:: Example Usage
    :color: secondary
    :icon: code

    .. tab-set::

        .. tab-item:: cURL
            :sync: key1

            .. code-block:: bash
                :linenos:

                curl --location --request GET 'http://{hostname}:5000/font/TotallyRealFont' \
                --header 'key: SuperSecretAPIKey'

        .. tab-item:: Node.JS
            :sync: key2

            .. code-block:: javascript
                :linenos:

                var request = require('request');
                var options = {
                    'method': 'GET',
                    'url': 'http://{{hostname}}:5000/font/TotallyRealFont',
                    'headers': {
                        'key': 'SuperSecretAPIKey'
                    }
                };
                request(options, function (error, response) {
                    if (error) throw new Error(error);
                    console.log(response.body);
                });

        .. tab-item:: Python
            :sync: key3

            .. code-block:: python
                :linenos:

                import requests

                url = "http://{hostname}:5000/font/TotallyRealFont"

                payload={}
                headers = {
                    'key': 'SuperSecretAPIKey'
                }

                response = requests.request("GET", url, headers=headers, data=payload)

                with open("TotallyRealFont.otf", "wb") as f:
                    f.write(response.content)

Get List of Base Fonts
-------------------------

:bdg-primary:`GET` /base-fonts

**Authorization** ``API Key in Header``

.. list-table::
    :header-rows: 1
    :align: left

    * - Key
      - Value
      - Requirement
    * - key
      - <value>
      - :code:`Required`

.. dropdown:: Example Usage
    :color: secondary
    :icon: code

    .. tab-set::

        .. tab-item:: cURL
            :sync: key1

            .. code-block:: bash
                :linenos:

                curl --location --request GET 'http://{hostname}:5000/base-fonts' \
                --header 'key: SuperSecretAPIKey'

        .. tab-item:: Node.JS
            :sync: key2

            .. code-block:: javascript
                :linenos:

                var request = require('request');
                var options = {
                    'method': 'GET',
                    'url': 'http://{{hostname}}:5000/base-fonts',
                    'headers': {
                        'key': 'SuperSecretAPIKey'
                    }
                };
                request(options, function (error, response) {
                    if (error) throw new Error(error);
                    console.log(response.body);
                });

        .. tab-item:: Python
            :sync: key3

            .. code-block:: python
                :linenos:

                import requests

                url = "http://{hostname}:5000/base-fonts"

                payload={}
                headers = {
                    'key': 'SuperSecretAPIKey'
                }

                response = requests.request("GET", url, headers=headers, data=payload)

                print(response.text)

Get List of Available Templates
---------------------------------

:bdg-primary:`GET` /templates

**Authorization** ``API Key in Header``

.. list-table::
    :header-rows: 1
    :align: left

    * - Key
      - Value
      - Requirement
    * - key
      - <value>
      - :code:`Required`

.. dropdown:: Example Usage
    :color: secondary
    :icon: code

    .. tab-set::

        .. tab-item:: cURL
            :sync: key1

            .. code-block:: bash
                :linenos:

                curl --location --request GET 'http://{hostname}:5000/templates' \
                --header 'key: SuperSecretAPIKey'

        .. tab-item:: Node.JS
            :sync: key2

            .. code-block:: javascript
                :linenos:

                var request = require('request');
                var options = {
                    'method': 'GET',
                    'url': 'http://{{hostname}}:5000/templates',
                    'headers': {
                        'key': 'SuperSecretAPIKey'
                    }
                };
                request(options, function (error, response) {
                    if (error) throw new Error(error);
                    console.log(response.body);
                });

        .. tab-item:: Python
            :sync: key3

            .. code-block:: python
                :linenos:

                import requests

                url = "http://{hostname}:5000/templates"

                payload={}
                headers = {
                    'key': 'SuperSecretAPIKey'
                }

                response = requests.request("GET", url, headers=headers, data=payload)

                print(response.text)

Generate a render of a template
--------------------------------

:bdg-primary:`GET` /render-template/<template_name>

**Authorization** ``API Key in Header``

.. list-table::
    :header-rows: 1
    :align: left

    * - Key
      - Value
      - Requirement
    * - key
      - <value>
      - :code:`Required`

.. dropdown:: Example Usage
    :color: secondary
    :icon: code

    .. tab-set::

        .. tab-item:: cURL
            :sync: key1

            .. code-block:: bash
                :linenos:

                curl --location --request GET 'http://{hostname}:5000/render-template/english_upperlower.csv' \
                --header 'key: SuperSecretAPIKey'

        .. tab-item:: Node.JS
            :sync: key2

            .. code-block:: javascript
                :linenos:

                var request = require('request');
                var options = {
                    'method': 'GET',
                    'url': 'http://{{hostname}}:5000/render-template/english_upperlower.csv',
                    'headers': {
                        'key': 'SuperSecretAPIKey'
                    }
                };
                request(options, function (error, response) {
                    if (error) throw new Error(error);
                    console.log(response.body);
                });

        .. tab-item:: Python
            :sync: key3

            .. code-block:: python
                :linenos:

                import requests

                url = "http://{hostname}:5000/render-template/english_upperlower.csv"

                payload={}
                headers = {
                    'key': 'SuperSecretAPIKey'
                }

                response = requests.request("GET", url, headers=headers, data=payload)

                print(response.text)

Identify Character
-------------------------

.. warning:: 

    This endpoint is currently in development.

:bdg-primary:`POST` /identify_character

**Authorization** ``API Key in Header``

.. list-table::
    :header-rows: 1
    :align: left

    * - Key
      - Value
      - Requirement
    * - key
      - <value>
      - :code:`Required`

``key`` is the API key set in the :doc:`config`, be sure to
specify the key in the header of the request.

**Body** ``form-data``

.. list-table::
    :header-rows: 1
    :align: left

    * - Key
      - Value
      - Requirement
    * - image
      - image_file
      - :code:`Required`

``image`` is the individual character to be identified.

.. dropdown:: Example Usage
    :color: secondary
    :icon: code

    .. tab-set::

        .. tab-item:: cURL
            :sync: key1

            .. code-block:: bash
                :linenos:

                curl --location --request POST 'http://{hostname}:5000/identify_character' \
                --header 'key: SuperSecretAPIKey' \
                --form 'image=@"/C:/Users/BookMarked/scans/c.png"'

        .. tab-item:: Node.JS
            :sync: key2

            .. code-block:: javascript
                :linenos:

                var request = require('request');
                var fs = require('fs');
                var options = {
                    'method': 'POST',
                    'url': 'http://{hostname}:5000/identify_character',
                    'headers': {
                        'key': 'SuperSecretAPIKey'
                    },
                    formData: {
                        'image': {
                            'value': fs.createReadStream('/C:/Users/BookMarked/scans/c.png'),
                            'options': {
                                'filename': '/C:/Users/BookMarked/scans/c.png',
                                'contentType': null
                            }
                        }
                    }
                };
                request(options, function (error, response) {
                    if (error) throw new Error(error);
                    console.log(response.body);
                });


        .. tab-item:: Python
            :sync: key3

            .. code-block:: python
                :linenos:

                import requests

                url = "http://hostname:5000/identify_character"

                payload={}
                files=[
                    ('image',('c.png',open('/C:/Users/BookMarked/scans/c.png','rb'),'image/png'))
                ]
                headers = {
                    'key': 'SuperSecretAPIKey'
                }

                response = requests.request("POST", url, headers=headers, data=payload, files=files)

                print(response.text)
