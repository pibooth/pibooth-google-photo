# -*- coding: utf-8 -*-

"""Pibooth plugin for google gallery upload."""

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.credentials import Credentials
import json
import os.path
import requests
import pibooth
from pibooth.utils import LOGGER

__version__ = "0.0.1"


###########################################################################
## HOOK pibooth
###########################################################################
def pibooth_configure(cfg):
    """Declare the new configuration options"""
    cfg.add_option('GOOGLE', 'album_name', "Pibooth",
                   "The name of album on gallery")
    cfg.add_option('GOOGLE', 'client_id_file', 'client_id.json',
                   "The client_id.json file download from google API")


@pibooth.hookimpl
def pibooth_startup(app, cfg):
    """Create the GoogleUpload instances."""
    try:
        app.google_photo = GoogleUpload(client_id=cfg.get('GOOGLE', 'client_id_file'),
                                        credentials=None)
    except KeyError as e:
        LOGGER.error("No GOOGLE:client_id_file detected on pibooth config file")


@pibooth.hookimpl
def state_processing_exit(app, cfg):
    """Upload picture to google photo album"""
    name = app.previous_picture_file
    try:
        google_name = cfg.get('GOOGLE', 'album_name')
    except KeyError as e:
        LOGGER.warning("No gallery name detected, use default value 'Pibooth'")
        google_name = "Pibooth"
    app.google_photo.upload_photos([name], google_name)


###########################################################################
## Class
################0###########################################################
class GoogleUpload(object):

    def __init__(self, client_id=None, credentials=None):
        self.scopes = ['https://www.googleapis.com/auth/photoslibrary',
                       'https://www.googleapis.com/auth/photoslibrary.sharing']

        # file to store authorization
        self.google_credentials = credentials
        # file with YOUR_CLIENT_ID and YOUR_CLIENT_SECRET generate on google
        self.client_id_file = client_id
        self.credentials = None
        self.session = None
        self.album_id = None
        self.album_name = None
        if not os.path.exists(self.client_id_file) or os.path.getsize(self.client_id_file) == 0:
            LOGGER.error("Can't load json file \'%s\'", self.client_id_file)
        self._get_authorized_session()

    def _is_internet(self):
        try:
            requests.get('https://www.google.com/').status_code
            return True
        except:
            LOGGER.warning("No internet connection!!!!")
            return False

    def _auth(self):
        """open browser to create credentials"""
        flow = InstalledAppFlow.from_client_secrets_file(
            self.client_id_file,
            scopes=self.scopes)

        self.credentials = flow.run_local_server(host='localhost',
                                                 port=8080,
                                                 authorization_prompt_message="",
                                                 success_message='The auth flow is complete; you may close this window.',
                                                 open_browser=True)

    def _get_authorized_session(self):

        # check the default path of save credentials to allow keep None
        if self.google_credentials is None:
            self.google_credentials = os.path.join(os.path.dirname(self.client_id_file) + "/google_credentials.dat")
        # if first instance of application:
        if not os.path.exists(self.google_credentials) or \
                os.path.getsize(self.google_credentials) == 0:
            self._auth()
            self.session = AuthorizedSession(self.credentials)
            LOGGER.debug("First run of application create credentials file %s", self.google_credentials)
            try:
                self._save_cred()
            except OSError as err:
                LOGGER.debug("Could not save auth tokens - %s", err)
        else:
            try:
                self.credentials = Credentials.from_authorized_user_file(self.google_credentials, self.scopes)
                self.session = AuthorizedSession(self.credentials)
            except ValueError:
                LOGGER.debug("Error loading auth tokens - Incorrect format")

    def _save_cred(self):
        if self.credentials:
            cred_dict = {
                'token': self.credentials.token,
                'refresh_token': self.credentials.refresh_token,
                'id_token': self.credentials.id_token,
                'scopes': self.credentials.scopes,
                'token_uri': self.credentials.token_uri,
                'client_id': self.credentials.client_id,
                'client_secret': self.credentials.client_secret
            }

            with open(self.google_credentials, 'w') as f:
                print(json.dumps(cred_dict), file=f)

    def get_albums(self, appCreatedOnly=False):
        """#Generator to loop through all albums"""
        params = {
            'excludeNonAppCreatedData': appCreatedOnly
        }
        while True:
            albums = self.session.get('https://photoslibrary.googleapis.com/v1/albums', params=params).json()
            LOGGER.debug("Server response: %s", albums)
            if 'albums' in albums:
                for a in albums["albums"]:
                    yield a
                if 'nextPageToken' in albums:
                    params["pageToken"] = albums["nextPageToken"]
                else:
                    return
            else:
                return

    def _create_or_retrieve_album(self):
        """Find albums created by this app to see if one matches album_title"""
        if self.album_name and self.album_id is None:
            for a in self.get_albums(True):
                if a["title"].lower() == self.album_name.lower():
                    self.album_id = a["id"]
                    LOGGER.info("Uploading into EXISTING photo album -- \'%s\'", self.album_name)
        if self.album_id is None:
            # No matches, create new album
            create_album_body = json.dumps({"album": {"title": self.album_name}})
            # print(create_album_body)
            resp = self.session.post('https://photoslibrary.googleapis.com/v1/albums', create_album_body).json()
            LOGGER.debug("Server response: %s", resp)
            if "id" in resp:
                LOGGER.info("Uploading into NEW photo album -- \'%s\'", self.album_name)
                self.album_id = resp['id']
            else:
                LOGGER.error("Could not find or create photo album \'{0}\'.\
                            Server Response: %s", self.album_name, resp)
                self.album_id = None

    def upload_photos(self, photo_file_list, album_name):
        self.album_name = album_name
        self._create_or_retrieve_album()

        # interrupt upload if an upload was requested but could not be created
        if self.album_name and not self.album_id or self._is_internet():
            LOGGER.error("Interrupt upload see previous error!!!!")
            return

        self.session.headers["Content-type"] = "application/octet-stream"
        self.session.headers["X-Goog-Upload-Protocol"] = "raw"

        for photo_file_name in photo_file_list:

            try:
                photo_file = open(photo_file_name, mode='rb')
                photo_bytes = photo_file.read()
            except OSError as err:
                LOGGER.error("Could not read file \'%s\' -- %s", photo_file_name, err)
                continue

            self.session.headers["X-Goog-Upload-File-Name"] = os.path.basename(photo_file_name)

            LOGGER.info("Uploading photo -- \'%s\'", photo_file_name)

            upload_token = self.session.post('https://photoslibrary.googleapis.com/v1/uploads', photo_bytes)

            if (upload_token.status_code == 200) and upload_token.content:

                create_body = json.dumps({"albumId": self.album_id, "newMediaItems": [
                    {"description": "", "simpleMediaItem": {"uploadToken": upload_token.content.decode()}}]}, indent=4)

                resp = self.session.post('https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate',
                                         create_body).json()

                LOGGER.debug("Server response: %s", resp)

                if "newMediaItemResults" in resp:
                    status = resp["newMediaItemResults"][0]["status"]
                    if status.get("code") and (status.get("code") > 0):
                        LOGGER.error("Could not add \'%s\' to library -- %s", os.path.basename(photo_file_name),
                                     status["message"])
                    else:
                        LOGGER.info(
                            "Added \'%s\' to library and album \'%s\' ", os.path.basename(photo_file_name),
                            album_name)
                else:
                    LOGGER.error(
                        "Could not add \'%s\' to library. Server Response -- %s", os.path.basename(photo_file_name),
                        resp)

            else:
                LOGGER.error("Could not upload \'%s\'. Server Response - %s", os.path.basename(photo_file_name),
                             upload_token)

        try:
            del (self.session.headers["Content-type"])
            del (self.session.headers["X-Goog-Upload-Protocol"])
            del (self.session.headers["X-Goog-Upload-File-Name"])
        except KeyError:
            pass
