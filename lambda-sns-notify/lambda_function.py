import json
import boto3
import os

def connect_to_aws(region, service):
    client = boto3.client(service, region_name = region)
    return client


def publish_to_sns(message, subject, topic_arn):
    client = connect_to_aws("us-east-1", "sns")

    response = client.publish(
        TopicArn=topic_arn,
        Message=message,
        Subject=subject,
    )
    print(response)


def parser_sqs_message(event):
    parsed_dict = {}
    try:
        body_json = event
        records = body_json["Records"][0]["body"]
        records = records.replace("'", '"')
        records = json.loads(records)
        
        parsed_dict['Bucket'] = records["Bucket"]
        parsed_dict['Object'] = records["Object"]
        print(parsed_dict)
        return parsed_dict
    except Exception as e:
        raise e


def lambda_handler(event, context):
    topic_arn = os.getenv("TOPIC_ARN", 
        "arn:aws:sns:us-east-1:936068047509:satellite_notification_topic")
    sqs_message = parser_sqs_message(event)
    print(sqs_message)

    message_subject = "Crowd Detected!"
    message_body = f"Crowded detected in Bucket: {sqs_message.get('Bucket')} and Object: {sqs_message.get('Object')}"

    try:
        publish_to_sns(message_body, message_subject, topic_arn)
        return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda!')
        }
    except Exception as e:
        return f"Error {str(e)}"