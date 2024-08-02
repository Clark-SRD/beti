import re
import io
import os
import json
import boto3
from PyPDF2 import PdfReader
from aws_lambda_powertools import Logger

s3 = boto3.client('s3')
lambda_client = boto3.client('lambda')
logger = Logger()
destination_function_arn = os.environ['DESTINATION_ARN']

@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    input_bucket = event['inputBucket']
    file_name = event['inputFileName']

    all_text, section3 = get_text_from_pdf(input_bucket, file_name)

    output_event = {
        'inputBucket': input_bucket,
        'outputBucket': event['outputBucket'],
        'inputFileName': file_name,
        'allText': all_text,
        'section3': section3
    }
    response = lambda_client.invoke(
        FunctionName=destination_function_arn,
        InvocationType='Event',
        Payload=json.dumps(output_event)
    )

    print("Invoked Function: ", destination_function_arn)
    return output_event

def get_text_from_pdf(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    pdf_file = response['Body'].read()
    reader = PdfReader(io.BytesIO(pdf_file))

    all_text = []
    section3_text = []
    capturing = False

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        if text:
            lines = text.split('\n')  # Split text into lines for line-by-line processing
            for line in lines:
                all_text.append(line + '\n')  # Collect all text
                if re.search(r'3.*EXECUTION', line, re.IGNORECASE):
                    capturing = True
                if capturing:
                    section3_text.append(line + '\n')

    full_text = ''.join(all_text)
    section3_full_text = ''.join(section3_text)
    return full_text, section3_full_text

