import boto3
sqs = boto3.client('sqs', region_name='us-east-1')  

def receive_messages_from_sqs(queue_url, max_number=1, visibility_timeout=30):
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=max_number,
        VisibilityTimeout=visibility_timeout
    )
    messages = response.get('Messages', [])
    for message in messages:
        message_body = message['Body']
        
        if 'MessageAttributes' in message:
            message_attributes = message['MessageAttributes']
            print(f"Received message with ID '{message['MessageId']}':")
            print(f"  Body: {message_body}")
            print("  Attributes:")
            for attr_name, attr_value in message_attributes.items():
                print(f"    {attr_name}: {attr_value['StringValue']} ({attr_value['DataType']})")
        else:
            print(f"Received message with ID '{message['MessageId']}':")
            print(f"  Body: {message_body}")
            print("  No MessageAttributes found.")
        delete_message_from_sqs(queue_url, message['ReceiptHandle'])

def delete_message_from_sqs(queue_url, receipt_handle):
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )
    print(f"Deleted message with ReceiptHandle: {receipt_handle}")

queue_url = 'https://sqs.us-east-1.amazonaws.com/851725305422/Rohan'
receive_messages_from_sqs(queue_url)
