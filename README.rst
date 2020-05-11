
====================
pibooth-google-photo
====================

|PythonVersions| |PypiPackage| |Downloads|

``pibooth-google-photo`` is a plugin for the `pibooth <https://github.com/pibooth/pibooth>`_
application.

It add the upload of pictures to `google photo gallery <https://photos.google.com/>`_

Install
-------

::

    $ pip3 install pibooth-google-photo


Obtaining a Google Photos API key
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Obtain a Google Photos API key (Client ID and Client Secret) by following the instructions on \
`Getting started with Google Photos REST APIs <https://developers.google.com/photos/library/guides/get-started>`_

**NOTE** When selecting your application type in Step 4 of "Request an OAuth 2.0 client ID", please select "Other". There's also no need to carry out step 5 in that section.

Configuration
-------------

This is the extra configuration options that can be added in the ``pibooth``
configuration):

.. code-block:: ini

    [GOOGLE]
    # The name of album on gallery
    album_name = Pibooth
    # The client_id.json file download from google API
    client_id_file = path/to/client_id.json

.. note:: Edit the configuration by running the command ``pibooth --config``.


Note
-----
At first connection allow application to use google photo with open browser windows


``client_id.json is like this``

.. code-block:: json

   {
   "installed":
       {
           "client_id":"8723982792-sdjfhdkjhvfkd76.apps.googleusercontent.com",
           "client_secret":"HJAHZhjhi_HJI789798giEdPIbJ",
           "auth_uri":"https://accounts.google.com/o/oauth2/auth",
           "token_uri":"https://www.googleapis.com/oauth2/v3/token",
           "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
           "redirect_uris":["urn:ietf:wg:oauth:2.0:oob","http://localhost"]
       }
   }



.. |PythonVersions| image:: https://img.shields.io/badge/python-2.7+ / 3.6+-red.svg
   :target: https://www.python.org/downloads
   :alt: Python 2.7+/3.6+

.. |PypiPackage| image:: https://badge.fury.io/py/pibooth-google-photo.svg
   :target: https://pypi.org/project/pibooth-google-photo
   :alt: PyPi package

.. |Downloads| image:: https://img.shields.io/pypi/dm/pibooth-google-photo?color=purple
   :target: https://pypi.org/project/pibooth-google-photo
   :alt: PyPi downloads