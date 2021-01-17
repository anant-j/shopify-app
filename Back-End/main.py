import os
import json
import random
import string
from flask import Flask, redirect, request, jsonify, session, make_response
from flask_cors import CORS, cross_origin
from flask_discord import DiscordOAuth2Session, requires_authorization
from requests_oauthlib import OAuth2Session
from werkzeug.utils import secure_filename
import firebase_handler as storage
import clarifai_handler as clarifai

my_directory = os.path.dirname(os.path.abspath(__file__))

with open(my_directory + '/secrets.json', 'r') as myfile:
    data = myfile.read()
obj = json.loads(data)

app = Flask(__name__)
app.debug = True
app.secret_key = obj["OAUTH2_CLIENT_SECRET"]
app.config["DISCORD_CLIENT_ID"] = obj["OAUTH2_CLIENT_ID"]
app.config["DISCORD_CLIENT_SECRET"] = obj["OAUTH2_CLIENT_SECRET"]
app.config["DISCORD_REDIRECT_URI"] = obj["Callback"]
# app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif', '.jpeg']
websiteAddress = obj["WebAddress"]
redirectAddress = obj["RedirectAddress"]

API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discord.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

CORS(app, support_credentials=True)

if 'http://' in app.config["DISCORD_REDIRECT_URI"]:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'


def token_updater(token):
    session['oauth2_token'] = token


def make_session(token=None, state=None, scope=None):
    return OAuth2Session(
        client_id=app.config["DISCORD_CLIENT_ID"],
        token=token,
        state=state,
        scope=scope,
        redirect_uri=app.config["DISCORD_REDIRECT_URI"],
        auto_refresh_kwargs={
            'client_id': app.config["DISCORD_CLIENT_ID"],
            'client_secret': app.config["DISCORD_CLIENT_SECRET"],
        },
        auto_refresh_url=TOKEN_URL,
        token_updater=token_updater)


discord = DiscordOAuth2Session(app)


@app.route('/')
def noapi():
    return redirect(redirectAddress)


@app.route("/login")
@cross_origin(supports_credentials=True,
              allow_headers=['Content-Type',
                             'Access-Control-Allow-Credentials'],
              origins=websiteAddress)
def login():
    scope = request.args.get(
        'scope',
        'email identify')
    discord = make_session(scope=scope.split(' '))
    authorization_url, state = discord.authorization_url(
        AUTHORIZATION_BASE_URL)
    session['DISCORD_OAUTH2_STATE'] = state
    return (authorization_url)


@app.route("/callback")
@cross_origin(supports_credentials=True)
def callback():
    try:
        discord.callback()
        return redirect(redirectAddress)
    except Exception:
        return redirect(redirectAddress)


@app.route("/userdata")
@cross_origin(supports_credentials=True,
              allow_headers=['Content-Type',
                             'Access-Control-Allow-Origin'],
              origins=websiteAddress)
@requires_authorization
def userData():
    try:
        if(discord.authorized):
            user = discord.fetch_user()
            email = user.email
            data = storage.getUserStats(email)
            resp = make_response(jsonify(email=email, stats=data))
            return resp
        else:
            return ("Unauthorized", 401)
    except Exception as e:
        return (str(e))


@app.route("/userimages")
@cross_origin(supports_credentials=True,
              allow_headers=['Content-Type',
                             'Access-Control-Allow-Origin'],
              origins=websiteAddress)
@requires_authorization
def userImages():
    try:
        if(discord.authorized):
            user = discord.fetch_user()
            email = user.email
            result = storage.list_img_urls_where("uploader", email)
            return (",".join(result))
        else:
            return ("Unauthorized", 401)
    except Exception as e:
        return (str(e))


@app.route("/get_all_sfw")
@cross_origin(supports_credentials=True,
              allow_headers=['Content-Type',
                             'Access-Control-Allow-Origin'],
              origins=websiteAddress)
def get_sfw_images():
    result = storage.list_img_urls_where("type", "SFW")
    return (",".join(result))


@app.route("/get_all_nsfw")
@cross_origin(supports_credentials=True,
              allow_headers=['Content-Type',
                             'Access-Control-Allow-Origin'],
              origins=websiteAddress)
@requires_authorization
def get_nsfw_images():
    try:
        if(discord.authorized):
            result = storage.list_img_urls_where("type", "NSFW")
            return (",".join(result))
        else:
            return ("Unauthorized", 401)
    except Exception as e:
        return (str(e))


@app.route("/upload", methods=['POST'])
@cross_origin(supports_credentials=True,
              allow_headers=['Content-Type',
                             'Access-Control-Allow-Origin'],
              origins=websiteAddress)
@requires_authorization
def uploadimg():
    try:
        if(discord.authorized):
            user = discord.fetch_user()
            email = user.email
            uploaded_file = request.files["uploadedfile"]
            original_filename = secure_filename(uploaded_file.filename)
            filename = random_name_gen()
            while (storage.blob_exists(filename)):
                filename = random_name_gen()
            if original_filename != '':
                file_ext = os.path.splitext(original_filename)[1]
                if file_ext.lower() not in app.config['UPLOAD_EXTENSIONS']:
                    return "Invalid image", 400
                else:
                    filename = filename + file_ext
            tempblob = storage.get_blob("temp/" + filename)
            storage.upload_to_storage(tempblob, uploaded_file)
            tempblob.make_public()
            NSFW = clarifai.is_NSFW(tempblob.public_url)
            tempblob.delete()
            uploaded_file.seek(0)
            data = storage.getAllUserData(email)
            if("stats" not in data):
                data["stats"] = {}
                data["stats"]["total"] = 0
                data["stats"]["nsfw_count"] = 0
                data["stats"]["sfw_count"] = 0
            if("images" not in data):
                data["images"] = []
            blob = storage.get_blob(filename)
            storage.upload_to_storage(blob, uploaded_file)
            blob.make_public()
            if(NSFW):
                metadata = {'type': 'NSFW', 'uploader': email,
                            "filename": original_filename}
                blob.metadata = metadata
                data["stats"]["total"] += 1
                data["stats"]["nsfw_count"] += 1
            else:
                metadata = {'type': 'SFW', 'uploader': email,
                            "filename": original_filename}
                blob.metadata = metadata
                data["stats"]["total"] += 1
                data["stats"]["sfw_count"] += 1
            data["images"].append(filename)
            blob.content_type = "image/" + file_ext[1:]
            blob.patch()
            storage.set_db(email, data)
            return redirect(redirectAddress + "/my")
        else:
            return ("Unauthorized", 401)
    except Exception as e:
        return (str(e))


@app.route("/delete")
@cross_origin(supports_credentials=True,
              allow_headers=['Content-Type',
                             'Access-Control-Allow-Origin'],
              origins=websiteAddress)
@requires_authorization
def delete_image():
    try:
        if(discord.authorized):
            user = discord.fetch_user()
            email = user.email
            imageid = request.args.get('id')
            data = storage.getAllUserData(email)
            for blob in storage.get_blobs_list():
                if (blob.metadata["uploader"] ==
                        email and blob.name == imageid):
                    if(blob.metadata["type"] == "NSFW"):
                        data["stats"]["nsfw_count"] -= 1
                    else:
                        data["stats"]["sfw_count"] -= 1
                    data["stats"]["total"] -= 1
                    data["images"].remove(imageid)
                    blob.delete()
            storage.set_db(email, data)
            return (str(redirectAddress + "/my"))
        else:
            return ("Unauthorized", 401)
    except Exception as e:
        return (str(e))


@app.route('/logout')
@cross_origin(supports_credentials=True,
              allow_headers=['Content-Type',
                             'Access-Control-Allow-Credentials',
                             'Access-Control-Allow-Origin'],
              origins=websiteAddress)
def logout():
    discord.revoke()
    session.clear()
    resp = make_response("Logged out")
    return (resp)


@app.errorhandler(404)
def page_not_found(e):
    return (redirect(redirectAddress))


@app.errorhandler(500)
def internal_server_error(e):
    return (redirect(redirectAddress))


def random_name_gen():
    return (
        ''.join(
            random.choices(
                string.ascii_uppercase +
                string.digits +
                string.ascii_lowercase,
                k=32)))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
