import boto3
import json
import base64

lambda_client = boto3.client(
    'lambda',
    region_name='eu',
    endpoint_url='http://localhost:4574'
)
""" :type : pyboto3.lambda_ """

data = {'data': 20}

response = lambda_client.invoke(
  FunctionName='process_kinesis',
  InvocationType='Event',
  Payload=json.dumps(data),
)

result = json.loads((response['Payload'].read()))
print(result['result'])