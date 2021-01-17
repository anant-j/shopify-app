from google.cloud import storage
from firebase_admin import credentials, firestore, initialize_app

cred = credentials.Certificate('cred.json')
default_app = initialize_app(cred)
db = firestore.client()

repo = cred.project_id+".appspot.com"
client = storage.Client.from_service_account_json('cred.json')
bucket = client.get_bucket(repo)


def getUserStats(email):
    doc_ref = db.collection(u'users').document(email)
    doc = doc_ref.get()
    if doc.exists:
        return(doc.to_dict()["stats"])
    return ({})


def getAllUserData(email):
    doc_ref = db.collection(u'users').document(email)
    doc = doc_ref.get()
    if doc.exists:
        return(doc.to_dict())
    return ({})


def blob_exists(filename):
    blob = bucket.blob(filename)
    return blob.exists()


def set_db(email, data):
    db.collection(u'users').document(email).set(data)
    return("DONE")


def list_img_urls_where(metadata, data):
    results_list = []
    for blob in client.list_blobs(repo):
        blob.make_public()
        if (blob.metadata[metadata] == data):
            results_list.append(str(blob.public_url))
    return results_list


def get_blob(url):
    return (bucket.blob(url))


def get_blobs_list():
    return (client.list_blobs(repo))


def upload_to_storage(blob, file):
    blob.upload_from_file(file, client=client)


def print_cred():
    return("Dones")


print_cred()
