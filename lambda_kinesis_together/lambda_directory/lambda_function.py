import base64
import requests


def lambda_handler(event, context):
    for record in event['Records']:
        #Kinesis data is base64 encoded so decode here
        data = int(base64.b64decode(record["kinesis"]["data"]))
        print(data)
        requests.post(url='http://localhost:5000/messages/', data={'data': data*data})

