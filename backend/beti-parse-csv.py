import json
import csv
import boto3
from io import StringIO

def lambda_handler(event, context):
    input_bucket = event.get('inputBucket')
    output_bucket = event.get('outputBucket')
    file_name = event.get('inputFileName')
    output_dict = event.get('output_dict', {})
    
    # Create CSV content
    csv_output = StringIO()
    csv_writer = csv.writer(csv_output, quoting=csv.QUOTE_MINIMAL)

    # The header row has been removed as per your request
    
    # Write the content
    for key in output_dict:
        entry = output_dict[key]
        spec_section_number = entry.get('specSectionNumber', '')
        spec_section_name = entry.get('specSectionName', '')
        test_type = entry.get('test_type', '')
        referenced_test_code = entry.get('referenced_test_code', '')
        frequency_quantity = entry.get('frequency_quantity', '')
        specific_requirements = entry.get('specific_requirements', '')
        responsible_entity = entry.get('responsible_entity', '')
        
        # Normalize new lines and carriage returns for CSV output
        spec_section_name = spec_section_name.replace("\n", " ").replace("\r", " ")
        test_type = test_type.replace("\n", " ").replace("\r", " ")
        referenced_test_code = referenced_test_code.replace("\n", " ").replace("\r", " ")
        frequency_quantity = frequency_quantity.replace("\n", " ").replace("\r", " ")
        specific_requirements = specific_requirements.replace("\n", " ").replace("\r", " ")
        responsible_entity = responsible_entity.replace("\n", " ").replace("\r", " ")

        # Include the new empty columns BECx_Required, Spec_Required, and Started/Completed
        becx_required = ""  # This will always be empty as per your requirement
        spec_required = ""  # Empty string for Spec_Required
        started_completed = ""  # Empty string for Started/Completed

        csv_writer.writerow([
            becx_required, spec_required, started_completed,
            spec_section_number, spec_section_name, test_type, referenced_test_code,
            frequency_quantity, specific_requirements, responsible_entity
        ])

    # Save the CSV content to S3
    s3_client = boto3.client('s3')
    s3_client.put_object(
        Bucket=output_bucket,
        Key=file_name.replace(".pdf", ".csv"),
        Body=csv_output.getvalue()
    )
    
    output_event = {
        'inputBucket': input_bucket,
        'outputBucket': output_bucket,
        'outputFileName': file_name.replace(".pdf", ".csv"),
        'output_csv': csv_output.getvalue()
    }
    
    return output_event

