import boto3

client = boto3.client(
    'lambda',
    region_name='eu',
    endpoint_url='http://localhost:4574'
)
""" :type : pyboto3.lambda_ """

iam_client = boto3.client('iam')
""" :type : pyboto3.iam """
#role = iam_client.get_role(RoleName='LambdaBasicExecution')

with open('lambda_directory/lambda.zip', 'rb') as f:
    zipped_code = f.read()

target_function_name = 'process_kinesis'

client.delete_function(FunctionName=target_function_name)

client.create_function(
    FunctionName=target_function_name,
    Runtime='python3.6',
    Role='fake_arn',
    Handler='lambda_function.lambda_handler_simple',
    Code=dict(ZipFile=zipped_code),
    Timeout=1,
    Environment=dict(Variables=dict())
)

