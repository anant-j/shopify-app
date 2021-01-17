import os
import json
from clarifai.rest import ClarifaiApp

my_directory = os.path.dirname(os.path.abspath(__file__))

with open(my_directory + '/secrets.json', 'r') as myfile:
    data = myfile.read()
obj = json.loads(data)

api_key = obj.get('Clarifai_API_Key')
model_id = obj.get('Clarifai_Model_Id')


def is_NSFW(img_url):
    app = ClarifaiApp(api_key=api_key)
    model = app.models.get(model_id=model_id)
    response = model.predict_by_url(url=img_url)
    sfw_score = 0
    nsfw_score = 0
    if(response["outputs"][0]["data"]["concepts"][0]["name"] == "sfw"):
        sfw_score = response["outputs"][0]["data"]["concepts"][0]["value"]
        nsfw_score = response["outputs"][0]["data"]["concepts"][1]["value"]
    elif(response["outputs"][0]["data"]["concepts"][0]["name"] == "nsfw"):
        nsfw_score = response["outputs"][0]["data"]["concepts"][0]["value"]
        sfw_score = response["outputs"][0]["data"]["concepts"][1]["value"]
    if(nsfw_score > sfw_score):
        return True
    else:
        return False
