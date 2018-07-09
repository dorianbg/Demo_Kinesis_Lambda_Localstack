import base64


def lambda_handler_simple(event, context):
    payload = event['data']
    return {'result': payload*payload}
