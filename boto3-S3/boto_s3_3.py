import boto3
import logging
import json
import uuid
import re
from botocore.exceptions import ClientError

class BucketWrapper:

    def __init__(self, bucket_name=None, region_name='us-east-1'):
        
        self.bucket_name = bucket_name
        self.region_name = region_name

        self.session = boto3.Session(region_name=region_name)
        self.s3_client = self.session.client('s3')
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def create_unique_bucket(self):
        bucket_name = self.generate_valid_bucket_name()
        try:
            print(f"Creating bucket '{bucket_name}' in region '{self.region_name}'...")
            if self.region_name == 'us-east-1':
                self.s3_client.create_bucket(Bucket=bucket_name)
            else:
                self.s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region_name}
                )
            print(f"Bucket '{bucket_name}' created successfully.")
            self.logger.info("Created bucket '%s' in region=%s", bucket_name, self.region_name)
            return bucket_name
        except ClientError as e:
            self.logger.exception("Couldn't create bucket named '%s' in region=%s.", bucket_name, self.region_name)
            print(f"Error: Couldn't create bucket named '{bucket_name}' in region '{self.region_name}'.")
            print(e)
            return None

    def generate_valid_bucket_name(self):
        bucket_name = f"mybucket-{uuid.uuid4().hex[:8]}"
        while not self.is_valid_bucket_name(bucket_name):
            bucket_name = f"mybucket-{uuid.uuid4().hex[:8]}"
        
        return bucket_name

    @staticmethod
    def is_valid_bucket_name(bucket_name):
        # Check if bucket name is between 3 and 63 characters long
        if len(bucket_name) < 3 or len(bucket_name) > 63:
            return False
        
        # Check if bucket name contains only lowercase letters, numbers, dots, and hyphens
        if not re.match("^[a-z0-9][a-z0-9.-]*[a-z0-9]$", bucket_name):
            return False
        
        # Check if bucket name does not contain two adjacent periods
        if ".." in bucket_name:
            return False
        
        # Check if bucket name does not resemble an IP address
        if re.match(r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", bucket_name):
            return False
        
        return True

    def put_policy(self, bucket_name, policy):
        try:
            print(f"Applying policy to bucket '{bucket_name}'...")
            self.s3_client.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps(policy)
            )
            print(f"Policy applied successfully to bucket '{bucket_name}'.")
            self.logger.info("Put policy %s for bucket '%s'.", policy, bucket_name)
        except ClientError as e:
            self.logger.exception("Couldn't apply policy to bucket '%s'.", bucket_name)
            print(f"Error: Couldn't apply policy to bucket '{bucket_name}'.")
            if e.response['Error']['Code'] == 'AccessDenied':
                print("Access Denied: Please check your AWS IAM permissions.")
            else:
                print(e)

    def put_lifecycle_configuration(self, bucket_name, lifecycle_rules):
        try:
            print(f"Applying lifecycle configuration to bucket '{bucket_name}'...")
            self.s3_client.put_bucket_lifecycle_configuration(
                Bucket=bucket_name,
                LifecycleConfiguration={'Rules': lifecycle_rules}
            )
            print(f"Lifecycle configuration applied successfully to bucket '{bucket_name}'.")
            self.logger.info("Put lifecycle rules %s for bucket '%s'.", lifecycle_rules, bucket_name)
        except ClientError as e:
            self.logger.exception("Couldn't put lifecycle rules for bucket '%s'.", bucket_name)
            print(f"Error: Couldn't put lifecycle rules for bucket '{bucket_name}'.")
            print(e)

    def enable_encryption(self, bucket_name):
        try:
            print(f"Enabling encryption for bucket '{bucket_name}'...")
            self.s3_client.put_bucket_encryption(
                Bucket=bucket_name,
                ServerSideEncryptionConfiguration={
                    'Rules': [
                        {
                            'ApplyServerSideEncryptionByDefault': {
                                'SSEAlgorithm': 'AES256'
                            }
                        }
                    ]
                }
            )
            print(f"Encryption enabled successfully for bucket '{bucket_name}'.")
            self.logger.info("Enabled encryption for bucket '%s'.", bucket_name)
        except ClientError as e:
            self.logger.exception("Couldn't enable encryption for bucket '%s'.", bucket_name)
            print(f"Error: Couldn't enable encryption for bucket '{bucket_name}'.")
            print(e)

    def put_object(self, bucket_name, key, local_file_path):
        try:
            print(f"Uploading file '{local_file_path}' to bucket '{bucket_name}' with key '{key}'...")
            self.s3_client.upload_file(
                Filename=local_file_path,
                Bucket=bucket_name,
                Key=key
            )
            print(f"File '{local_file_path}' uploaded successfully to bucket '{bucket_name}' with key '{key}'.")
            self.logger.info("Uploaded file '%s' to bucket '%s' with key '%s'.", local_file_path, bucket_name, key)
        except ClientError as e:
            self.logger.exception("Couldn't upload file '%s' to bucket '%s'.", local_file_path, bucket_name)
            print(f"Error: Couldn't upload file '{local_file_path}' to bucket '{bucket_name}'.")
            print(e)
        except FileNotFoundError as e:
            self.logger.exception("The file '%s' was not found.", local_file_path)
            print(f"Error: The file '{local_file_path}' was not found.")
            print(e)

if __name__ == "__main__":
    try:
        # Initialize BucketWrapper
        bucket_wrapper = BucketWrapper(region_name='us-east-1')
        
        # Create a unique bucket
        print("Attempting to create a unique bucket...")
        bucket_name = bucket_wrapper.create_unique_bucket()
        
        if bucket_name:
            print(f"Unique bucket '{bucket_name}' created successfully.")

            # Apply a bucket policy (replace {...} with your actual policy)
            print(f"Applying policy to bucket '{bucket_name}'...")
            policy=({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": [
                        "s3:GetObject"
                    ],
                    "Resource": [
                        f"arn:aws:s3:::{bucket_name}/*"
                    ]
                }
            ]
        })
            print(f"Policy application process completed.")

            # Put lifecycle configuration
            print(f"Applying lifecycle configuration to bucket '{bucket_name}'...")
            bucket_wrapper.put_lifecycle_configuration(
                bucket_name,
                [
                    {
                        'ID': 'Archive and delete after 365 days',
                        'Prefix': '',
                        'Status': 'Enabled',
                        'Transitions': [
                            {
                                'Days': 365,
                                'StorageClass': 'GLACIER'
                            }
                        ],
                        'Expiration': {
                            'Days': 365 * 2
                        }
                    }
                ]
            )
            print(f"Lifecycle configuration application process completed.")
            bucket_wrapper.enable_encryption(bucket_name)
            print(f"Encryption enablement process completed.")

            # Upload an object to the bucket
            key = 's3_create.py' 
            local_file_path = 'C:/Users/rohan/Downloads/Boto3/s3/s3_create.py' 
            print(f"Attempting to upload file '{local_file_path}' to bucket '{bucket_name}' with key '{key}'...")
            bucket_wrapper.put_object(bucket_name, key, local_file_path)
            print(f"File upload process completed.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
