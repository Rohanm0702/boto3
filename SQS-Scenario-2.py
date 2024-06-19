def send_message_to_sqs(queue_url, message_body, message_attributes=None):
    import boto3
    sqs = boto3.client('sqs', region_name='us-east-1')  
    message_attributes = message_attributes or {}
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=message_body,
        MessageAttributes=message_attributes
    )
    print(f"Sent message with ID: {response['MessageId']} to queue: {queue_url}")

queue_url = 'https://sqs.us-east-1.amazonaws.com/851725305422/Rohan'
message_body = 'boto3 lab exercise'
message_attributes = {
    'Author': {
        'StringValue': 'Rohan',
        'DataType': 'String'
    },
    'Priority': {
        'StringValue': 'High',
        'DataType': 'String'
    }
}
send_message_to_sqs(queue_url, message_body, message_attributes)
