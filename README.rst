********************
pibooth-google-photo
********************

Pibooth plugin to add the upload of pictures to google photo 

Setup
-----

Installing python library dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
::

       $ sudo pip3 install google-auth-oauthlib

Obtaining a Google Photos API key
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Obtain a Google Photos API key (Client ID and Client Secret) by following the instructions on \
[Getting started with Google Photos REST APIs](https://developers.google.com/photos/library/guides/get-started)

**NOTE** When selecting your application type in Step 4 of "Request an OAuth 2.0 client ID", please select "Other". There's also no need to carry out step 5 in that section.

Configure Pibooth to use google api
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1 clone or download the plugin

.. code-block:: bash
    git clone https://github.com/pibooth/pibooth-google-photo.git

1. Open client_id.json file
2. Replace `YOUR_CLIENT_ID` in the client_id.json file with the provided Client ID.
3. Replace `YOUR_CLIENT_SECRET` in the client_id.json file with the provided Client Secret.

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

4. Append plugin path to pibooth config

.. code-block:: ini

    # Path to a custom pibooth plugin (list of paths accepted)
    plugins = path/to/pibooth-google-photo/pibooth_google_plugin.py

6. At first connection allow application to use google photo with open browser windows
