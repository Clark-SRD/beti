import json
import boto3
import os
import urllib.parse
from aws_lambda_powertools import Logger

logger = Logger()
s3 = boto3.client('s3')
bucket = os.environ['BUCKET']

@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    try:
        # Extract the file name from the event object
        file_name_encoded = event['queryStringParameters']['file']
        # Decode the file name
        file_name = urllib.parse.unquote_plus(file_name_encoded)

        key = file_name  # Using file name directly without stage folder

        response = s3.get_object(Bucket=bucket, Key=key)
        file_content = response['Body'].read().decode('utf-8')

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': file_content
        }
    except Exception as e:
        # Log the error and return an error response
        logger.error(f'Error downloading file: {e}')
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(f'Error: {str(e)}')
        }

