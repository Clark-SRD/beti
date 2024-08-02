import json
import boto3
import os
from botocore.exceptions import ClientError
from aws_lambda_powertools import Logger

logger = Logger()
s3 = boto3.client('s3')

@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    try:
        bucket_name = os.environ['BUCKET']
        
        file_name = event['queryStringParameters']['file']
        key = file_name  # Using file name directly without stage folder
        URL = s3.generate_presigned_url('put_object', Params={'Bucket': bucket_name, 'Key': key, 'ContentType': 'application/pdf'}, ExpiresIn=3600)

        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT',
            'Content-Type': 'application/json'
        }

        output_event = {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'URL': URL})
        }

        return output_event

    except ClientError as e:
        logger.error(f'Error generating pre-signed URL: {e}')
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }
