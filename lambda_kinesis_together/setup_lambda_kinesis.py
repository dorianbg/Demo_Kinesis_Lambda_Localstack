import configparser
import boto3
import json
import time
import logging
logging.basicConfig(filename='main.log', level=20)

# PART 0 - LOAD CONFIG AND CREATE CLIENTS
config = configparser.ConfigParser()
config_file_name = 'aws.ini'
config.read(config_file_name)

logging.info('Read config file')
logging.info('Config content is', config)

kinesis_client = boto3.client(
    'kinesis',
    region_name='eu',
    endpoint_url='http://localhost:4568',
)
""" :type : pyboto3.kinesis """

lambda_client = boto3.client(
    'lambda',
    region_name='eu',
    endpoint_url='http://localhost:4574'
)
""" :type : pyboto3.lambda_ """

lambda_function_name = config['lambda']['function_name']
kinesis_stream_name = config['kinesis']['stream_name']
kinesis_stream_arn = config['kinesis']['stream_arn']

# PART 1 - Create a Lambda function
create_lambda_function = config['general']['create_lambda_function']

if create_lambda_function:
    # 1 delete lambda function if already exists
    if any(lambda_function_name == lambda_f['FunctionName'] for lambda_f in lambda_client.list_functions()['Functions']):
        lambda_client.delete_function(FunctionName='process_kinesis')
        logging.info('Deleted function ' + lambda_function_name)

    # 2 create new lambda function
    lambda_zipped_code_location = config['lambda']['zipped_code_location']
    with open(lambda_zipped_code_location, 'rb') as f:
        zipped_code = f.read()
        logging.info('Successfully read the ZIP file')

    lambda_handler = config['lambda']['handler']

    lambda_client.create_function(
        FunctionName=lambda_function_name,
        Runtime='python3.6',
        Role='fake_arn',
        Handler=lambda_handler,
        Code=dict(ZipFile=zipped_code),
        Timeout=1,
        Environment=dict(Variables=dict())
    )
    logging.info('Successfully created the lambda function')


# PART 2 - Create a Kinesis stream
create_kinesis_stream = config['general']['create_kinesis_stream']

if create_kinesis_stream:
    # find number of shards if creating a new stream
    num_shards = int(config['kinesis']['num_shards'])
    logging.info('Number of shards is ' + str(num_shards))

    # delete if already exsits
    if kinesis_stream_name in kinesis_client.list_streams()['StreamNames']:
        logging.info('Found an existing stream with name' + kinesis_stream_name)
        kinesis_client.delete_stream(StreamName=kinesis_stream_name)
        logging.info('Deleted the existing stream with name' + kinesis_stream_name)
        time.sleep(1)

    kinesis_client.create_stream(StreamName=kinesis_stream_name, ShardCount=num_shards)
    logging.info('Created a new stream')
    time.sleep(0.5)
    kinesis_stream_arn = kinesis_client.describe_stream(StreamName=kinesis_stream_name)['StreamDescription']['StreamARN']
    logging.info('Received the ARN of the stream:' + kinesis_stream_arn)

    config['kinesis']['stream_arn'] = kinesis_stream_arn
    with open(config_file_name, 'w') as configfile:  # save
        config.write(configfile)
    logging.info('Wrote the ARN to config file')

# PART 3 - Link Kinesis as event source of Lambda
link_kinesis_with_lambda = config['general']['link_kinesis_with_lambda']

if link_kinesis_with_lambda:
    if any(lambda_function_name == lambda_f['FunctionName'] for lambda_f in lambda_client.list_functions()['Functions'])\
            and any(kinesis_stream_name == existing_kinesis_stream_name for existing_kinesis_stream_name in kinesis_client.list_streams()['StreamNames']):
        logging.info('Found a lambda function with name' + lambda_function_name)

        lambda_batch_size = config['lambda']['batch_size']
        lambda_client.create_event_source_mapping(

            EventSourceArn=kinesis_stream_arn,
            FunctionName=lambda_function_name,
            Enabled=True,
            BatchSize=100,
            StartingPosition='TRIM_HORIZON'
        )
        logging.info('Created the mapping between lambda function ' + lambda_function_name + ' and kinesis stream ' + kinesis_stream_name)

# PART 4 - Load kinesis with Fake Records
load_kinesis_with_data = config['general']['load_kinesis_with_data']

if load_kinesis_with_data:
    for i in range(0, 500):
        kinesis_client.put_record(StreamName=kinesis_stream_name, Data=json.dumps(i), PartitionKey='key1')



'''
time.sleep(1)

shard_id = kinesis_client.describe_stream(StreamName=target_stream_name)['StreamDescription']['Shards'][0]['ShardId']

shard_iterator = kinesis_client.get_shard_iterator(StreamName=target_stream_name, ShardId=shard_id,
                                           ShardIteratorType='TRIM_HORIZON')

print(shard_iterator)

records = client.get_records(ShardIterator=shard_iterator['ShardIterator'])
for record in records['Records']:
    print(record)
'''
