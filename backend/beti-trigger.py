import boto3
import json
import os
from aws_lambda_powertools import Logger
from urllib.parse import unquote_plus  # Import unquote_plus for decoding

destination_function_arn = os.environ['DESTINATION_ARN']
input_bucket = os.environ['INPUT_BUCKET']
output_bucket = os.environ['OUTPUT_BUCKET']
lambda_client = boto3.client('lambda')
s3_client = boto3.client('s3')
logger = Logger()

@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key_encoded = event['Records'][0]['s3']['object']['key']
    file_name = unquote_plus(object_key_encoded)  # Decode the URL-encoded object key
    csv_file_name = file_name.replace('.pdf', '.csv')

    # Check if the file is a PDF
    if file_name.lower().endswith('.pdf'):

        # Check if the .csv file already exists in the exact folder of output_bucket
        response = s3_client.list_objects_v2(
            Bucket=output_bucket,
            Prefix=csv_file_name
        )

        # Check if the exact file exists
        file_exists = any(item['Key'] == csv_file_name for item in response.get('Contents', []))

        if file_exists:  # File already exists
            logger.info(f"File {csv_file_name} already exists in {output_bucket}. Skipping function invocation.")
            return {'status': 'File already exists, skipping invocation'}

        # Prepare payload for the next function if the file does not exist
        output_event = {
            'inputBucket': bucket_name,
            'inputFileName': file_name,
            'outputBucket': output_bucket,
            'outputFileName': csv_file_name
        }
        
        response = lambda_client.invoke(
            FunctionName=destination_function_arn,
            InvocationType='Event',
            Payload=json.dumps(output_event)
        )
        
        logger.info("Invoked Function: " + destination_function_arn)
        print("NVOKED FUNCTION: ", destination_function_arn)
        
        return output_event
    else:
        logger.info(f"File {file_name} is not a PDF. Skipping function invocation.")
        return {'status': 'File is not a PDF, skipping invocation'}

