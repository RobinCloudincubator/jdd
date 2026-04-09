import boto3
import json
import random
from load_inputs import load_input_json_by_folder, write_left_right_json
from datetime import datetime
# Name of the folder under comparisons/ (resolved next to load_inputs.py, not cwd).
EXPERIMENT_FOLDER = "improve_entry_model_comparison"
INFERENCE_PROFILE = 'arn:aws:bedrock:eu-west-1:594987468797:inference-profile/eu.anthropic.claude-sonnet-4-5-20250929-v1:0' # Anthropic Sonnet 4.5
INFERENCE_PROFILE_2 = 'arn:aws:bedrock:eu-west-1:594987468797:inference-profile/eu.amazon.nova-pro-v1:0' # Amazon Nova Pro

lambda_client = boto3.client('lambda')
inputs = load_input_json_by_folder(EXPERIMENT_FOLDER)

#generate random number
random_number = str(random.randint(100000, 999999))
# use timestamp as random number
keyValue = 'model_comparison_1'
callNo = keyValue + '_' + random_number + '_' + datetime.now().strftime("%Y%m%d%H%M%S")

for id, system in inputs.items():
    model_1_response = lambda_client.invoke(
        FunctionName="ag_ImproveCmdbEntry",
        InvocationType="RequestResponse",
        Payload=json.dumps(
            {
                "callNo": callNo + "_1",
                "keyValue": keyValue,
                "system_json": json.dumps(system),
                "inference_profile": INFERENCE_PROFILE,
            }
        ),
    )
    model_1_response = model_1_response['Payload'].read().decode('utf-8')
    model_1_response = json.loads(model_1_response)
    system_json = model_1_response['system_json']

    model_2_response = lambda_client.invoke(
        FunctionName="ag_ImproveCmdbEntry",
        InvocationType="RequestResponse",
        Payload=json.dumps(
            {
                "callNo": callNo + "_2",
                "keyValue": keyValue,
                "system_json": json.dumps(system),
                "inference_profile": INFERENCE_PROFILE_2,
            }
        ),
    )
    model_2_response = model_2_response['Payload'].read().decode('utf-8')
    model_2_response = json.loads(model_2_response)
    system_json_2 = model_2_response['system_json']
    write_left_right_json(EXPERIMENT_FOLDER, id, system_json, system_json_2)