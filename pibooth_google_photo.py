# -*- coding: utf-8 -*-

"""Pibooth plugin for Google Photos upload."""

import json
import os.path

import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.credentials import Credentials

import pibooth
from pibooth.utils import LOGGER


__version__ = "1.0.2"


###########################################################################
# HOOK pibooth
###########################################################################

@pibooth.hookimpl
def pibooth_configure(cfg):
    """Declare the new configuration options"""
    cfg.add_option('GOOGLE', 'activate', True,
                   "Enable upload on Google Photos",
                   "Enable upload", ['True', 'False'])
    cfg.add_option('GOOGLE', 'album_name', "Pibooth",
                   "Album where pictures are uploaded",
                   "Album name", "Pibooth")
    cfg.add_option('GOOGLE', 'client_id_file', '',
                   "Credentials file downloaded from Google API")


@pibooth.hookimpl
def pibooth_startup(app, cfg):
    """Create the GoogleUpload instance."""
    activate_state = cfg.getboolean('GOOGLE', 'activate')
    app.google_photo = GoogleUpload(client_id=cfg.getpath('GOOGLE', 'client_id_file'),
                                    credentials=None, activate=activate_state)


@pibooth.hookimpl
def state_processing_exit(app, cfg):
    """Upload picture to google photo album"""
    name = app.previous_picture_file
    google_name = cfg.get('GOOGLE', 'album_name')
    activate_state = cfg.getboolean('GOOGLE', 'activate')
    app.google_photo.upload_photos([name], google_name, activate_state)


###########################################################################
# Class
###########################################################################


class GoogleUpload(object):

    def __init__(self, client_id=None, credentials=None, activate=True):
        """Initialize GoogleUpload instance

        :param client_id: file download from google API
        :type client_id: file
        :param credentials: file create at first run to keep allow API use
        :type credentials: file
        :param activate: use to disable the plugin
        :type activate: bool
        """
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
        self.activate = activate
        if not os.path.exists(self.client_id_file) or os.path.getsize(self.client_id_file) == 0:
            LOGGER.error(
                "Can't load json file '%s' please check GOOGLE:client_id_file on pibooth config file (DISABLE PLUGIN)", self.client_id_file)
            self.activate = False
        if self.activate and self._is_internet():
            self._get_authorized_session()

    def _is_internet(self):
        """check internet connexion"""
        try:
            requests.get('https://www.google.com/').status_code
            return True
        except requests.ConnectionError:
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
        """Check if credentials file exists"""
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
        "save credentials file next to client id file to keep use API without allow acces"
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

            with open(self.google_credentials, 'w') as fp:
                json.dump(cred_dict, fp)

    def get_albums(self, app_created_only=False):
        """Generator to loop through all albums"""
        params = {
            'excludeNonAppCreatedData': app_created_only
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
                    LOGGER.info("Uploading into EXISTING photo album -- '%s'", self.album_name)
        if self.album_id is None:
            # No matches, create new album
            create_album_body = json.dumps({"album": {"title": self.album_name}})
            # print(create_album_body)
            resp = self.session.post('https://photoslibrary.googleapis.com/v1/albums', create_album_body).json()
            LOGGER.debug("Server response: %s", resp)
            if "id" in resp:
                LOGGER.info("Uploading into NEW photo album -- '%s'", self.album_name)
                self.album_id = resp['id']
            else:
                LOGGER.error("Could not find or create photo album '%s'.\
                             Server Response: %s", self.album_name, resp)
                self.album_id = None

    def upload_photos(self, photo_file_list, album_name, activate):
        """Funtion use to upload list of photos to google album

        :param photo_file_list: list of photos name with full path
        :type photo_file_list: file
        :param album_name: name of albums to upload
        :type album_name: str
        :param activate: use to disable the upload
        :type activate: bool
        """
        self.activate = activate
        # interrupt upload no internet
        if not self._is_internet():
            LOGGER.error("Interrupt upload no internet connexion!!!!")
            return
        # if plugin is disable
        if not self.activate:
            return
        # plugin is disable at startup but activate after so check credential file
        elif not self.credentials:
            self._get_authorized_session()

        self.album_name = album_name
        self._create_or_retrieve_album()

        # interrupt upload if no album id can't read or create
        if self.album_name and not self.album_id:
            LOGGER.error("Interrupt upload album not found!!!!")
            return

        self.session.headers["Content-type"] = "application/octet-stream"
        self.session.headers["X-Goog-Upload-Protocol"] = "raw"

        for photo_file_name in photo_file_list:

            try:
                photo_file = open(photo_file_name, mode='rb')
                photo_bytes = photo_file.read()
            except OSError as err:
                LOGGER.error("Could not read file '%s' -- %s", photo_file_name, err)
                continue

            self.session.headers["X-Goog-Upload-File-Name"] = os.path.basename(photo_file_name)

            LOGGER.info("Uploading photo -- '%s'", photo_file_name)

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
                        LOGGER.error("Could not add '%s' to library -- %s", os.path.basename(photo_file_name),
                                     status["message"])
                    else:
                        LOGGER.info(
                            "Added '%s' to library and album '%s' ", os.path.basename(photo_file_name),
                            album_name)
                else:
                    LOGGER.error(
                        "Could not add '%s' to library. Server Response -- %s", os.path.basename(photo_file_name),
                        resp)

            else:
                LOGGER.error("Could not upload '%s'. Server Response -- %s", os.path.basename(photo_file_name),
                             upload_token)

        try:
            del self.session.headers["Content-type"]
            del self.session.headers["X-Goog-Upload-Protocol"]
            del self.session.headers["X-Goog-Upload-File-Name"]
        except KeyError:
            pass
