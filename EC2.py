import boto3
from datetime import datetime
import pytz
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

logs = boto3.client('logs')
log_group_name = '/lab/log'
log_stream_name_start = 'start_instances'
log_stream_name_stop = 'stop_instances'

def setup_log_group_and_stream():
    try:
        logs.create_log_group(logGroupName=log_group_name)
    except logs.exceptions.ResourceAlreadyExistsException:
        logger.info(f'Log group {log_group_name} already exists')

    try:
        logs.create_log_stream(logGroupName=log_group_name, logStreamName=log_stream_name_start)
    except logs.exceptions.ResourceAlreadyExistsException:
        logger.info(f'Log stream {log_stream_name_start} already exists')

    try:
        logs.create_log_stream(logGroupName=log_group_name, logStreamName=log_stream_name_stop)
    except logs.exceptions.ResourceAlreadyExistsException:
        logger.info(f'Log stream {log_stream_name_stop} already exists')

def log_to_cloudwatch(log_stream_name, message):
    logs.put_log_events(
        logGroupName=log_group_name,
        logStreamName=log_stream_name,
        logEvents=[
            {
                'timestamp': int(datetime.now(pytz.utc).timestamp() * 1000),
                'message': message
            }
        ]
    )

def ec2_tag(instance_ids, start_schedule, stop_schedule, auto_start_stop):
    ec2 = boto3.client('ec2')

    tags = [
        {'Key': 'StartSchedule', 'Value': start_schedule},
        {'Key': 'StopSchedule', 'Value': stop_schedule},
        {'Key': 'AutoStartStop', 'Value': auto_start_stop}
    ]

    ec2.create_tags(Resources=instance_ids, Tags=tags)

def start_instances():
    ec2 = boto3.resource('ec2')
    current_time = datetime.now(pytz.utc).strftime('%H:%M')

    filters = [
        {'Name': 'tag:AutoStartStop', 'Values': ['True']},
        {'Name': 'tag:StartSchedule', 'Values': [current_time]}
    ]

    instances = ec2.instances.filter(Filters=filters)

    started_any_instance = False

    for instance in instances:
        if instance.state['Name'] == 'stopped':
            instance.start()
            started_any_instance = True
            message = f'Started instance: {instance.id}'
            logger.info(message)
            log_to_cloudwatch(log_stream_name_start, message)

    if not started_any_instance:
        message = f'No instances to start at {current_time}'
        logger.info(message)
        log_to_cloudwatch(log_stream_name_start, message)

def stop_instances():
    ec2 = boto3.resource('ec2')
    current_time = datetime.now(pytz.utc).strftime('%H:%M')

    filters = [
        {'Name': 'tag:AutoStartStop', 'Values': ['True']},
        {'Name': 'tag:StopSchedule', 'Values': [current_time]}
    ]

    instances = ec2.instances.filter(Filters=filters)

    stopped_any_instance = False

    for instance in instances:
        if instance.state['Name'] == 'running':
            instance.stop()
            stopped_any_instance = True
            message = f'Stopped instance: {instance.id}'
            logger.info(message)
            log_to_cloudwatch(log_stream_name_stop, message)

    if not stopped_any_instance:
        message = f'No instances to stop at {current_time}'
        logger.info(message)
        log_to_cloudwatch(log_stream_name_stop, message)

if __name__ == "__main__":
    instance_ids = ['i-0076810de5951daee']  
    start_schedule = '17:43'
    stop_schedule = '17:47'
    auto_start_stop = 'True'

    setup_log_group_and_stream()
    ec2_tag(instance_ids, start_schedule, stop_schedule, auto_start_stop)
    start_instances()
    stop_instances()
