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

1. Save a client_id.json file and open
2. Replace `YOUR_CLIENT_ID` in the client_id.json file with the provided Client ID.
3. Replace `YOUR_CLIENT_SECRET` in the client_id.json file with the provided Client Secret.

``client_id.json``

.. code-block:: json

   {
   "installed":
       {
           "client_id":"YOUR_CLIENT_ID",
           "client_secret":"YOUR_CLIENT_SECRET",
           "auth_uri":"https://accounts.google.com/o/oauth2/auth",
           "token_uri":"https://www.googleapis.com/oauth2/v3/token",
           "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
           "redirect_uris":["urn:ietf:wg:oauth:2.0:oob","http://localhost"]
       }
   }

4. Replace `'path/to/client_id.json'` on `pibooth_google_photo.py` to the good path of your `client_id.json`
5. Append plugin to pibooth config
6. At first connection allow application to use google photo with open browser windows
