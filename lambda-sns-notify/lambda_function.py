import json
import boto3

from data import message

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

def parser_sqs_message(event):
    dict_event_parsed = {}
    try:
        body = event["Records"][0]["body"]
        body = body.replace("'", '"')

        body_json = json.loads(body)
        return body_json
    except Exception as e:
        raise e


def lambda_handler(event, context):
    # TODO implement
    topic_arn = "arn:aws:sns:us-east-1:066045871446:coronavirus-notification-topic"
    sqs_message = parser_sqs_message(message)
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
    

lambda_handler(None, None)