from google.cloud import storage
from firebase_admin import credentials, firestore, initialize_app

cred = credentials.Certificate('cred.json')
default_app = initialize_app(cred)
db = firestore.client()

repo = cred.project_id + ".appspot.com"
client = storage.Client.from_service_account_json('cred.json')
bucket = client.get_bucket(repo)


# Get user's statistics
def getUserStats(email):
    doc_ref = db.collection(u'users').document(email)
    doc = doc_ref.get()
    if doc.exists:
        return(doc.to_dict()["stats"])
    return ({})


# Get user's data
def getAllUserData(email):
    doc_ref = db.collection(u'users').document(email)
    doc = doc_ref.get()
    if doc.exists:
        return(doc.to_dict())
    return ({})


# Check if the image already exists in storage
def blob_exists(filename):
    blob = bucket.blob(filename)
    return blob.exists()


# Updates the database for given user with the provided data
def update_db(email, data):
    db.collection(u'users').document(email).set(data)
    return("DONE")


# Get a list of url's for images whose metadata's properties match the
# given data
def list_img_urls_where(metadata, data):
    results_list = []
    for blob in client.list_blobs(repo):
        blob.make_public()
        if ("temp" not in blob.name and blob.metadata[metadata] == data):
            results_list.append(str(blob.public_url))
    return results_list


# Get the blob for provided url
def get_blob(url):
    return (bucket.blob(url))


# Returns a list of all blobs in storage
def get_blobs_list():
    return (client.list_blobs(repo))


# Upload file to storage for specified blob
def upload_to_storage(blob, file):
    blob.upload_from_file(file, client=client)
