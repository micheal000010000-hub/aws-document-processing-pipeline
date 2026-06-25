import boto3

def lambda_handler(event, context):

    dynamodb = boto3.client(
        "dynamodb",
        endpoint_url="http://host.docker.internal:4566",
        region_name="us-east-1",
        aws_access_key_id="test",
        aws_secret_access_key="test"
    )

    tables = dynamodb.list_tables()

    return {
        "statusCode": 200,
        "body": str(tables)
    }
