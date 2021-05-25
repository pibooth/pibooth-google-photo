
====================
pibooth-google-photo
====================

|PythonVersions| |PypiPackage| |Downloads|

``pibooth-google-photo`` is a plugin for the `pibooth`_ application.

Its permits to upload the pictures to a `Google Photos`_ album. It requires an
internet connection.

Install
-------

::

    $ pip3 install pibooth-google-photo

Configuration
-------------

Here below the new configuration options available in the `pibooth`_ configuration.
**The keys and their default values are automatically added to your configuration after first** `pibooth`_ **restart.**

.. code-block:: ini

    [GOOGLE]

    # Album where pictures are uploaded
    album_name = Pibooth

    # Credentials file downloaded from Google API
    client_id_file =

.. note:: Edit the configuration by running the command ``pibooth --config``.

Grant secured access
--------------------

Access to a Google Photos album is granted by a **Credentials file** that shall
be defined in the ``[GOOGLE][client_id_file]`` configuration key. This file does
not contain your Google credentials and it can not be used by an other application
than `pibooth`_.

It contains the `Google Photos`_ API key (Client ID and Client Secret) generated
by following the instructions to
`enable the Google Photos Library API <https://developers.google.com/photos/library/guides/get-started>`_
(use the shortcut button).

:warning: When selecting the application type, please select **Desktop app**.

The content of the **Credentials file** looks like this:

.. code-block:: json

    {
        "installed":
            {
            "client_id": "8723982792-sdjfhdkjhvfkd76.apps.googleusercontent.com",
            "client_secret": "HJAHZhjhi_HJI789798giEdPIbJ",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://www.googleapis.com/oauth2/v3/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob","http://localhost"]
            }
    }

.. note:: At the first connection, allow ``pibooth`` to use `Google Photos`_ in
          the opened web browser window.

.. --- Links ------------------------------------------------------------------

.. _`pibooth`: https://pypi.org/project/pibooth

.. _`Google Photos`: https://photos.google.com

.. |PythonVersions| image:: https://img.shields.io/badge/python-2.7+ / 3.6+-red.svg
   :target: https://www.python.org/downloads
   :alt: Python 2.7+/3.6+

.. |PypiPackage| image:: https://badge.fury.io/py/pibooth-google-photo.svg
   :target: https://pypi.org/project/pibooth-google-photo
   :alt: PyPi package

.. |Downloads| image:: https://img.shields.io/pypi/dm/pibooth-google-photo?color=purple
   :target: https://pypi.org/project/pibooth-google-photo
   :alt: PyPi downloads
