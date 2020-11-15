# -*- coding: utf-8 -*-

"""Pibooth plugin to upload pictures on Google Photos."""

import json
import os.path

import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import AuthorizedSession, Request
from google.oauth2.credentials import Credentials

import pibooth
from pibooth.utils import LOGGER


__version__ = "1.0.2"


@pibooth.hookimpl
def pibooth_configure(cfg):
    """Declare the new configuration options"""
    cfg.add_option('GOOGLE', 'album_name', "Pibooth",
                   "Album where pictures are uploaded",
                   "Album name", "Pibooth")
    cfg.add_option('GOOGLE', 'client_id_file', '',
                   "Credentials file downloaded from Google API")


@pibooth.hookimpl
def pibooth_startup(app, cfg):
    """Create the GooglePhotosUpload instance."""
    app.google_photos = GooglePhotosApi(cfg.getpath('GOOGLE', 'client_id_file'))


@pibooth.hookimpl
def state_processing_exit(app, cfg):
    """Upload picture to google photo album"""
    pictures = (app.previous_picture_file,)
    app.google_photos.upload(pictures, cfg.get('GOOGLE', 'album_name'))


class GooglePhotosApi(object):

    """Class handling connections to Google Photos.

    A file with YOUR_CLIENT_ID and YOUR_CLIENT_SECRET is required, go to
    https://developers.google.com/photos/library/guides/get-started .

    A credentials file ``credentials_filename`` is generated at first run to store
    permanently the autorizations to us Google API.

    :param client_id: file generated from google API
    :type client_id: str
    :param credentials_filename: name of the file to store authorization
    :type credentials_filename: str
    """

    URL = 'https://photoslibrary.googleapis.com/v1'
    SCOPES = ['https://www.googleapis.com/auth/photoslibrary',
              'https://www.googleapis.com/auth/photoslibrary.sharing']

    def __init__(self, client_id_file, credentials_filename="google_credentials.dat"):
        self.client_id_file = client_id_file
        self.credentials_file = os.path.join(os.path.dirname(self.client_id_file), credentials_filename)

        self.activated = True
        if not os.path.exists(self.client_id_file) or os.path.getsize(self.client_id_file) == 0:
            if self.client_id_file:
                LOGGER.error("Can not load [GOOGLE][client_id_file]='%s' please check config",
                             self.client_id_file)
            self.activated = False

        self._albums_cache = {}  # Keep cache to avoid multiple request
        self._credentials = None
        if self.activated and self.is_reachable():
            self._session = self._get_authorized_session()
        else:
            self._session = None

    def _auth(self):
        """Open browser to create credentials."""
        flow = InstalledAppFlow.from_client_secrets_file(self.client_id_file, scopes=self.SCOPES)
        return flow.run_local_server(port=0)

    def _save_credentials(self, credentials):
        """Save credentials in a file to use API without need to allow acces."""
        with open(self.credentials_file, 'w') as fp:
            fp.write(credentials.to_json())

    def _get_authorized_session(self):
        """Create credentials file if required and open a new session."""
        if not os.path.exists(self.credentials_file) or \
                os.path.getsize(self.credentials_file) == 0:
            self._credentials = self._auth()
            LOGGER.debug("First use of pibooth-google-photo: generate credentials file %s", self.credentials_file)
            try:
                self._save_credentials(self._credentials)
            except OSError as err:
                LOGGER.warning("Can not save Google Photos credentials in '%s': %s", self.credentials_file, err)
        else:
            try:
                self._credentials = Credentials.from_authorized_user_file(self.credentials_file, self.SCOPES)
                if self._credentials.expired:
                    self._credentials.refresh(Request())
                    self._save_credentials(self._credentials)
            except ValueError:
                LOGGER.debug("Error loading Google Photos OAuth tokens: incorrect format")

        if self._credentials:
            return AuthorizedSession(self._credentials)
        return None

    def is_reachable(self):
        """Check if Google Photos is reachable."""
        try:
            return requests.get('https://photos.google.com').status_code == 200
        except requests.ConnectionError:
            return False

    def get_albums(self, app_created_only=False):
        """Generator to loop through all Google Photos albums."""
        params = {
            'excludeNonAppCreatedData': app_created_only
        }
        while True:
            albums = self._session.get(self.URL + '/albums', params=params).json()
            LOGGER.debug("Google Photos server response: %s", albums)

            if 'albums' in albums:
                for album in albums["albums"]:
                    yield album
                if 'nextPageToken' in albums:
                    params["pageToken"] = albums["nextPageToken"]
                else:
                    return  # close generator
            else:
                return  # close generator

    def get_album_id(self, album_name):
        """Return the album ID if exists else None."""
        if album_name.lower() in self._albums_cache:
            return self._albums_cache[album_name.lower()]["id"]

        for album in self.get_albums(True):
            title = album["title"].lower()
            self._albums_cache[title] = album
            if title == album_name.lower():
                LOGGER.info("Found existing Google Photos album '%s'", album_name)
                return album["id"]
        return None

    def create_album(self, album_name):
        """Create a new album and return its ID."""
        LOGGER.info("Creating a new Google Photos album '%s'", album_name)
        create_album_body = json.dumps({"album": {"title": album_name}})

        resp = self._session.post(self.URL + '/albums', create_album_body).json()
        LOGGER.debug("Google Photos server response: %s", resp)

        if "id" in resp:
            return resp['id']

        LOGGER.error("Can not create Google Photos album '%s'", album_name)
        return None

    def upload(self, photo_files, album_name):
        """Upload a list of pictures files to the given Google Photos album.

        :param photo_files: list of photos name with full path
        :type photo_files: file
        :param album_name: name of albums to upload
        :type album_name: str
        """
        if not self.activated:
            # Invalid credentials file
            return

        if not self.is_reachable():
            LOGGER.error("Google Photos upload failure: no internet connexion!")
            return

        if not self._credentials:
            # Plugin was disabled at startup but activated after
            self._session = self._get_authorized_session()

        album_id = self.get_album_id(album_name)
        if not album_id:
            album_id = self.create_album(album_name)
        if not album_id:
            LOGGER.error("Google Photos upload failure: album '%s' not found!", album_name)
            return

        self._session.headers["Content-type"] = "application/octet-stream"
        self._session.headers["X-Goog-Upload-Protocol"] = "raw"

        for filename in photo_files:

            try:
                with open(filename, mode='rb') as fp:
                    data = fp.read()
            except OSError as err:
                LOGGER.error("Google Photos upload failure: can not read file '%s': %s", filename, err)
                continue

            self._session.headers["X-Goog-Upload-File-Name"] = os.path.basename(filename)

            LOGGER.info("Uploading picture '%s' to Google Photos", filename)
            upload_token = self._session.post(self.URL + '/uploads', data)

            if upload_token.status_code == 200 and upload_token.content:

                create_body = json.dumps({"albumId": album_id,
                                          "newMediaItems": [
                                              {"description": "",
                                               "simpleMediaItem": {"uploadToken": upload_token.content.decode()}
                                              }
                                          ]}, indent=4)

                resp = self._session.post(self.URL + '/mediaItems:batchCreate', create_body).json()
                LOGGER.debug("Google Photos server response: %s", resp)

                if "newMediaItemResults" in resp:
                    status = resp["newMediaItemResults"][0]["status"]
                    if status.get("code") and (status.get("code") > 0):
                        LOGGER.error("Google Photos upload failure: can not add '%s' to library: %s",
                                     os.path.basename(filename), status["message"])
                    else:
                        LOGGER.info("Google Photos upload successful: '%s' added to album '%s'",
                                    os.path.basename(filename), album_name)
                else:
                    LOGGER.error("Google Photos upload failure: can not add '%s' to library",
                                 os.path.basename(filename))

            elif upload_token.status_code != 200:
                LOGGER.error("Google Photos upload failure: can not connect to '%s' (HTTP error %s)",
                             self.URL, upload_token.status_code)
            else:
                LOGGER.error("Google Photos upload failure: no response content from server '%s'",
                             self.URL)

        try:
            del self._session.headers["Content-type"]
            del self._session.headers["X-Goog-Upload-Protocol"]
            del self._session.headers["X-Goog-Upload-File-Name"]
        except KeyError:
            pass
