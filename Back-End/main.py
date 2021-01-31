# All Imports
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

with open(my_directory + '/secrets/secrets.json', 'r') as myfile:
    data = myfile.read()
obj = json.loads(data)

# Setting up application
app = Flask(__name__)
app.debug = False
CORS(app, support_credentials=True)

# Setting up Discord OAuth
app.secret_key = obj["OAUTH2_CLIENT_SECRET"]
app.config["DISCORD_CLIENT_ID"] = obj["OAUTH2_CLIENT_ID"]
app.config["DISCORD_CLIENT_SECRET"] = obj["OAUTH2_CLIENT_SECRET"]
app.config["DISCORD_REDIRECT_URI"] = obj["Callback"]
API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discord.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'
if 'http://' in app.config["DISCORD_REDIRECT_URI"]:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'

# Setting up Image criteria
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif', '.jpeg']

# Setting up API, Webapp & CORS criteria
websiteAddress = obj["WebAddress"]
redirectAddress = obj["RedirectAddress"]


# This function updates the Discord Oauth Tokens
def token_updater(token):
    session['oauth2_token'] = token


# Method to make a Discord OAuth session
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


# Redirect to webpage if API is called directly
@app.route('/')
def noapi():
    return redirect(redirectAddress)

# Status for health check
@app.route('/status')
def status():
    return ("up")


# Login endpoint
# Returns the login url that the webpage is redirected to.
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


# Callback endpoint
# Redirects to the webpage when called.
@app.route("/callback")
@cross_origin(supports_credentials=True)
def callback():
    try:
        discord.callback()
        return redirect(redirectAddress)
    except Exception:
        return redirect(redirectAddress)


# Userdata endpoint
# Returns users email, and upload statistics.
@app.route("/userdata")
@cross_origin(supports_credentials=True,
              allow_headers=['Content-Type',
                             'Access-Control-Allow-Origin'],
              origins=websiteAddress)
@requires_authorization
def userData():
    try:
        if(discord.authorized):  # If user is authorized/logged in
            email = str(discord.fetch_user()) # Get user's email address
            data = storage.getUserStats(email)
            resp = make_response(jsonify(email=email, stats=data))
            return resp
        else:
            # User is not logged in, or is unauthorized
            return ("Unauthorized", 401)
    except Exception as e:
        return (str(e))


# userimages endpoint
# Returns a comma seperated string containing links to all images uploaded
# by the user
@app.route("/userimages")
@cross_origin(supports_credentials=True,
              allow_headers=['Content-Type',
                             'Access-Control-Allow-Origin'],
              origins=websiteAddress)
@requires_authorization
def userImages():
    try:
        if(discord.authorized):  # If user is authorized/logged in
            email = str(discord.fetch_user()) # Get user's email address
            result = storage.list_img_urls_where("uploader", email)
            return (",".join(result))
        else:
            # User is not logged in, or is unauthorized
            return ("Unauthorized", 401)
    except Exception as e:
        return (str(e))


# get_all_sfw endpoint
# Returns a comma seperated string containing links to all SFW images
@app.route("/get_all_sfw")
@cross_origin(supports_credentials=True,
              allow_headers=['Content-Type',
                             'Access-Control-Allow-Origin'],
              origins=websiteAddress)
def get_sfw_images():
    try:
        result = storage.list_img_urls_where("type", "SFW")
        return (",".join(result))
    except Exception as e:
        return (str(e))


# get_all_nsfw endpoint
# Returns a comma seperated string containing links to all NSSFW images
@app.route("/get_all_nsfw")
@cross_origin(supports_credentials=True,
              allow_headers=['Content-Type',
                             'Access-Control-Allow-Origin'],
              origins=websiteAddress)
@requires_authorization
def get_nsfw_images():
    try:
        if(discord.authorized):  # If user is authorized/logged in
            result = storage.list_img_urls_where("type", "NSFW")
            return (",".join(result))
        else:
            # User is not logged in, or is unauthorized
            return ("Unauthorized", 401)
    except Exception as e:
        return (str(e))


# upload endpoint
# Redirects to "my" webpage on success, otherwise error status is returned.
@app.route("/upload", methods=['POST'])
@cross_origin(supports_credentials=True,
              allow_headers=['Content-Type',
                             'Access-Control-Allow-Origin'],
              origins=websiteAddress)
@requires_authorization
def uploadimg():
    try:
        if(discord.authorized):  # If user is authorized/logged in
            email = str(discord.fetch_user()) # Get user's email address
            # Get the uploaded file
            uploaded_file = request.files["uploadedfile"]
            # Get the uploaded file's name
            original_filename = secure_filename(uploaded_file.filename)
            # Generate a random (32 byte) filename
            filename = random_name_gen(32)
            # If given filename is already used,
            # regenerate until a unique one is generated
            while (storage.blob_exists(filename)):
                filename = random_name_gen(32)
            # Validate file extensions
            if original_filename != '':
                file_ext = os.path.splitext(original_filename)[1]
                if file_ext.lower() not in app.config['UPLOAD_EXTENSIONS']:
                    return "Invalid image", 400
                else:
                    # Add extension to 32 byte file name
                    filename = filename + file_ext
            # Create a temporary blob
            tempblob = storage.get_blob("temp/" + filename)
            # Upload file to temporary blob
            storage.upload_to_storage(tempblob, uploaded_file)
            tempblob.make_public()  # Make temporary blob publicly accessible
            # Get temporary blob's URL, send it through Clarifai's API
            NSFW = clarifai.is_NSFW(tempblob.public_url)
            tempblob.delete()  # Delete temporary blob
            # Set file pointer to initial index
            uploaded_file.seek(0)
            data = storage.getAllUserData(email)  # Get all User's data
            # If there are no stats for the user, set up the "stats" dictionary
            if("stats" not in data):
                data["stats"] = {}
                data["stats"]["total"] = 0
                data["stats"]["nsfw_count"] = 0
                data["stats"]["sfw_count"] = 0
            # If there is no "images" array for the user, set up array
            if("images" not in data):
                data["images"] = []
            blob = storage.get_blob(filename)  # Create blob for file
            # Upload file to the blob
            storage.upload_to_storage(blob, uploaded_file)
            blob.make_public()  # Make blob publicly accessible
            if(NSFW):  # If image is NSFW
                # Update metadata
                metadata = {'type': 'NSFW', 'uploader': email,
                            "filename": original_filename}
                blob.metadata = metadata
                data["stats"]["total"] += 1
                data["stats"]["nsfw_count"] += 1
            else:  # If image is SFW
                # Update metadata
                metadata = {'type': 'SFW', 'uploader': email,
                            "filename": original_filename}
                blob.metadata = metadata
                data["stats"]["total"] += 1
                data["stats"]["sfw_count"] += 1
            # Add images to user's "images" array
            data["images"].append(filename)
            # Set blob's content type
            blob.content_type = "image/" + file_ext[1:]
            blob.patch()  # Update blob's metadata
            # Update user's statistics and image array in firebase
            storage.update_db(email, data)
            return redirect(redirectAddress + "/my")
        else:
            # User is not logged in, or is unauthorized
            return ("Unauthorized", 401)
    except Exception as e:
        return (str(e))


# delete endpoint
# Redirects to "my" webpage on success, otherwise error status is returned
@app.route("/delete")
@cross_origin(supports_credentials=True,
              allow_headers=['Content-Type',
                             'Access-Control-Allow-Origin'],
              origins=websiteAddress)
@requires_authorization
def delete_image():
    try:
        if(discord.authorized):  # If user is authorized/logged in
            email = str(discord.fetch_user())  # Get user's email address
            imageid = request.args.get('id')  # Get requested image's id
            data = storage.getAllUserData(email)  # Get all User's data
            # For every blob in all images
            for blob in storage.get_blobs_list():
                # If image uploader is the same as requester, and
                # image name is the same as requested
                if (blob.metadata["uploader"] ==
                        email and blob.name == imageid):
                    if(blob.metadata["type"] == "NSFW"):  # If image is NSFW
                        data["stats"]["nsfw_count"] -= 1
                    else:  # If image is SFW
                        data["stats"]["sfw_count"] -= 1
                    data["stats"]["total"] -= 1
                    # Remove image from "images" array for user
                    data["images"].remove(imageid)
                    blob.delete()  # Delete image
            # Set storage in firebase with updated data
            storage.update_db(email, data)
            return (str(redirectAddress + "/my"))
        else:
            # User is not logged in, or is unauthorized
            return ("Unauthorized", 401)
    except Exception as e:
        return (str(e))


# logout endpoint
# Logs out user
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

# 404 error handler
@app.errorhandler(404)
def page_not_found(e):
    return (redirect(redirectAddress))


# 500 error handler
@app.errorhandler(500)
def internal_server_error(e):
    return (redirect(redirectAddress))


# Function to generate a random name consisting of
# Uppercase letters (A-Z)
# Lowecase letters (a-z)
# Numbers/Digits (0-9)
def random_name_gen(size):
    return (
        ''.join(
            random.choices(
                string.ascii_uppercase +
                string.digits +
                string.ascii_lowercase,
                k=size)))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
