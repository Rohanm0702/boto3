import boto3
sqs = boto3.client('sqs', region_name='us-east-1')  

def create_sqs_queue(queue_name):
    response = sqs.create_queue(
        QueueName=queue_name,
        Attributes={
            'DelaySeconds': '0', 
            'MessageRetentionPeriod': '172800',  
            'VisibilityTimeout': '30'  
        }
    )
    return response['QueueUrl']

queue_name = 'Rohan'
queue_url = create_sqs_queue(queue_name)
print(f"Created SQS queue '{queue_name}' with URL: {queue_url}")
