
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

Picture URL
-----------

Uploaded picture URL is set to ``app.previous_picture_url`` attribute at the end of
`processing` state (``state_processing_exit`` hook).

.. warning:: for security reason, URL is valid for only 1 hour.

Grant secured access
--------------------

Access to a Google Photos album is granted by a **Credentials file** that shall
be defined in the ``[GOOGLE][client_id_file]`` configuration key. This file does
not contain your Google credentials and it can not be used by an other application
than `pibooth`_.

It contains the `Google Photos`_ API key (Client ID and Client Secret) generated
by following the instructions:


===========  ==================================================================
 |step1|     `Go to Google Photos Library API <https://developers.google.com/photos/library/guides/get-started>`_
             and click on ``Enable the Google Photos Library API``.

 |step2|     Enter a project name (for instance **pibooth**) and click on
             ``NEXT``.

 |step3|     Enter a text to be displayed on user consent page when you will
             start ``pibooth`` with ``pibooth-google-photo`` enabled for the
             first time (for instance **Pibooth**) and click on ``NEXT``.

 |step4|     Select the application type: **Desktop app**.and click on
             ``CREATE``.

 |step5|     Download the credential file, save it somewhere accessible by
             `pibooth` and click on ``DONE``.
===========  ==================================================================

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

.. |PythonVersions| image:: https://img.shields.io/badge/python-3.6+-red.svg
   :target: https://www.python.org/downloads
   :alt: Python 3.6+

.. |PypiPackage| image:: https://badge.fury.io/py/pibooth-google-photo.svg
   :target: https://pypi.org/project/pibooth-google-photo
   :alt: PyPi package

.. |Downloads| image:: https://img.shields.io/pypi/dm/pibooth-google-photo?color=purple
   :target: https://pypi.org/project/pibooth-google-photo
   :alt: PyPi downloads

.. --- Tuto -------------------------------------------------------------------

.. |step1| image:: https://github.com/pibooth/pibooth-google-photo/blob/master/docs/images/step1_shortcut_button.png?raw=true
   :width: 80 %
   :alt: step1_shortcut_button

.. |step2| image:: https://github.com/pibooth/pibooth-google-photo/blob/master/docs/images/step2_project_name.png?raw=true
   :width: 80 %
   :alt: step2_project_name

.. |step3| image:: https://github.com/pibooth/pibooth-google-photo/blob/master/docs/images/step3_display_name.png?raw=true
   :width: 80 %
   :alt: step3_display_name

.. |step4| image:: https://github.com/pibooth/pibooth-google-photo/blob/master/docs/images/step4_app_type.png?raw=true
   :width: 80 %
   :alt: step4_app_type

.. |step5| image:: https://github.com/pibooth/pibooth-google-photo/blob/master/docs/images/step5_download.png?raw=true
   :width: 80 %
   :alt: step5_download
