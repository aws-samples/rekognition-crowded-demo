import json
import boto3
import os


def aws_connection(region, service):
    client = boto3.client(region_name = region, service_name = service)
    return client


def parser_sqs_message(event):
    dict_event_parsed = {}
    try:
        body = event["Records"][0]["body"]
        body = body.replace("'", '"')
        body_json = json.loads(body)

        body_sqs = body_json["Records"][0]["s3"]

        dict_event_parsed['Bucket'] = body_sqs["bucket"].get("name")
        dict_event_parsed['Object'] = body_sqs["object"].get("key")

        return dict_event_parsed
    except Exception as e:
        raise e


def rekognition_detect_crowd(client, s3_dict_info):
    bucket = s3_dict_info.get("Bucket")
    image = s3_dict_info.get("Object")

    try:
        response = client.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': image
                }
            },
            MinConfidence=70.0
        )
        return response
    except Exception as e:
        print(f"[Error] {e}")
        raise e


def check_if_crowded(rekognition_json):
    labels = rekognition_json["Labels"]
    crowded = False

    for label in labels:
        label_name = label['Name']
        if "Crowd" in label_name:
            label_confidence = label['Confidence']
            if float(label_confidence) > 80.0:
                crowded = True

    return crowded


def send_message_sqs(client, message, sqs_url):
    message = str(message)

    response = client.send_message(
            QueueUrl=sqs_url,
            MessageBody=message
    )
    print(response)


def lambda_handler(event, context):
    rekognition_client = aws_connection("us-east-1", "rekognition")
    sqs_client = aws_connection("us-east-1", "sqs")
    sqs_url = os.getenv("SQS_URL", "https://sqs.us-east-1.amazonaws.com/936068047509/rekognition_notify")

    sqs_data_parsed = parser_sqs_message(event)
    rekognition_json = rekognition_detect_crowd(rekognition_client, sqs_data_parsed)
    is_crowded = check_if_crowded(rekognition_json)
    
    if is_crowded:
        sqs_data_parsed['Success'] = "True"
        print(f"[INFO] Going to send to SQS Queue {sqs_data_parsed}")
        send_message_sqs(sqs_client, sqs_data_parsed, sqs_url)
        return {
            'statusCode': 200,
            'body': sqs_data_parsed
        }
    
    print("[INFO] Not going to send to SQS Queue")