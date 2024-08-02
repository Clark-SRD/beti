import json
import boto3
from botocore.exceptions import ClientError
import re
import os
from aws_lambda_powertools import Logger

logger = Logger()
s3 = boto3.client('s3')
lambda_client = boto3.client('lambda')
destination_function_arn = os.environ['DESTINATION_ARN']

@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    input_bucket = event['inputBucket']
    output_bucket = event['outputBucket']
    file_name = event['inputFileName']
    all_text = event['allText']
    section3 = event['section3']
    
    spec_section_number = extract_spec_section_number(file_name)
    
    spec_section_name = invoke_claude_instant(
        task="Return the spec section name from this pdf file name and return it in xml format <answer>Title</answer>.",
        text=file_name
    )
    
    test_types_response = invoke_claude_instant(
        task="""
        List all Test Types, Inspections, Field Visits, or Mockups mentioned within section 3 of the document in order. 
        Provide the list within xml format <answer>Test</answer>.
        """,
        text=all_text
    )
    
    test_types = extract_test_types(test_types_response)
    
    output_dict = {}

    for number, test_type in enumerate(test_types, start=1):
        referenced_test_code = invoke_claude_instant(
            task=f"Extract the referenced test codes for the test type '{test_type}' from the text.",
            text=all_text
        )
        
        frequency_quantity = invoke_claude_instant(
            task=f"Extract the frequency quantity for the test type '{test_type}' from the text.",
            text=all_text
        )
        
        specific_requirements = invoke_claude_instant(
            task=f"Extract any specific requirements for the test type '{test_type}' mentioned in the text.",
            text=all_text
        )
        
        responsible_entity = invoke_claude_instant(
            task=f"Extract the responsible entity for the test type '{test_type}' from the text.",
            text=all_text
        )

        output_dict[number] = {
            "specSectionNumber": spec_section_number,
            "specSectionName": parse_xml_answer(spec_section_name.strip()),
            "test_type": parse_xml_answer(test_type.strip()),
            "referenced_test_code": referenced_test_code.strip(),
            "frequency_quantity": frequency_quantity.strip(),
            "specific_requirements": specific_requirements.strip(),
            "responsible_entity": responsible_entity.strip()
        }
    
    output_event = {
        'inputBucket': input_bucket,
        'outputBucket': output_bucket,
        'inputFileName': file_name,
        'output_dict': output_dict
    }

    response = lambda_client.invoke(
        FunctionName=destination_function_arn,
        InvocationType='Event',
        Payload=json.dumps(output_event)
    )
    print("Invoked Function: ", destination_function_arn)

    return output_event

def invoke_claude_instant(task, text):
    prompt = f"System: {task} \n\nHuman: {text}\n\nAssistant:"
    bedrock_runtime = boto3.client("bedrock-runtime", "us-east-1")
    
    kwargs = {
      "modelId": "anthropic.claude-v2:1",
      "contentType": "application/json",
      "accept": "*/*",
      "body": json.dumps({"prompt": prompt,
                "max_tokens_to_sample":100000,
                "temperature":0.5,
                "top_k":250,
                "top_p":1,
                "stop_sequences":["\n\nHuman:"],
                "anthropic_version":"bedrock-2023-05-31"
      })
    }
    
    response = bedrock_runtime.invoke_model(**kwargs)
    response_body_str = response['body'].read().decode('utf-8')
    response_json = json.loads(response_body_str)
    completion = response_json.get("completion", "")
    return completion.strip()

def extract_spec_section_number(file_name):
    pattern = r'\b(?:\d{2}[- ]?\d{4}(?:\.\d{1,2})?)\b'
    spec_section_number = re.search(pattern, file_name)
    return spec_section_number.group() if spec_section_number else "Not found"

def extract_test_types(response):
    lines = response.split('\n')
    return [line.strip() for line in lines if line.strip()]


def parse_xml_answer(text):
    pattern = re.compile(r'<answer>(.*?)</answer>', re.DOTALL)
    answers = pattern.findall(text)
    return answers
