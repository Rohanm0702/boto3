import boto3
sqs = boto3.client('sqs', region_name='us-east-1')  

def send_message_to_sqs(queue_url, message_body, message_attributes=None):
    message_attributes = message_attributes or {}
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=message_body,
        MessageAttributes=message_attributes
    )
    print(f"Sent message with ID: {response['MessageId']} to queue: {queue_url}")

def receive_messages_from_sqs(queue_url, max_number=1, visibility_timeout=30):
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=max_number,
        VisibilityTimeout=visibility_timeout
    )
    messages = response.get('Messages', [])
    for message in messages:
        message_body = message['Body']
        receipt_handle = message['ReceiptHandle']
        print(f"Received message with ID '{message['MessageId']}' and ReceiptHandle '{receipt_handle}':")
        print(f"  Body: {message_body}")    
    return messages 

def change_message_visibility(queue_url, receipt_handle, visibility_timeout):
    try:
        response = sqs.change_message_visibility(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle,
            VisibilityTimeout=visibility_timeout
        )
        print(f"Changed visibility timeout for message with ReceiptHandle '{receipt_handle}' to {visibility_timeout} seconds")
    except sqs.exceptions.ReceiptHandleIsInvalid as e:
        print(f"Error: {e}")
        print(f"The receipt handle '{receipt_handle}' is invalid or the message associated with it may have been deleted or processed.")
    except Exception as e:
        print(f"Unexpected error: {e}")

def main():
    queue_url = 'https://sqs.us-east-1.amazonaws.com/851725305422/Rohan'
    
    message_body = 'Rohan Lab!'
    message_attributes = {
        'Author': {
            'StringValue': 'Rohan Lab SQS',
            'DataType': 'String'
        },
        'Priority': {
            'StringValue': 'High',
            'DataType': 'String'
        }
    }
    send_message_to_sqs(queue_url, message_body, message_attributes)
    messages = receive_messages_from_sqs(queue_url)
    if messages:
        receipt_handle = messages[0]['ReceiptHandle']
        new_visibility_timeout = 30
        change_message_visibility(queue_url, receipt_handle, new_visibility_timeout)

if __name__ == '__main__':
    main()
