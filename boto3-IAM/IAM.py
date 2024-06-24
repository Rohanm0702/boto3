import boto3
 
# Target account ID and role name
target_account_id = '381492154328'
role_name = 'Raghu-boto3'
 
# Function to assume a role in the target account
def assume_role(account_id, role_name):
    sts_client = boto3.client('sts')
    role_arn = f'arn:aws:iam::{account_id}:role/{role_name}'
    response = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName='AssumeRoleSession'
    )
    return response['Credentials']
 
# Function to list IAM users with active access keys
def list_iam_users_with_active_keys(credentials):
    iam_client = boto3.client(
        'iam',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )
    users_with_active_keys = []
    paginator = iam_client.get_paginator('list_users')
    for response in paginator.paginate():
        for user in response['Users']:
            access_keys = iam_client.list_access_keys(UserName=user['UserName'])['AccessKeyMetadata']
            for key in access_keys:
                if key['Status'] == 'Active':
                    users_with_active_keys.append({
                        'UserName': user['UserName'],
                        'AccessKeyId': key['AccessKeyId'],
                        'CreateDate': key['CreateDate'].strftime('%Y-%m-%dT%H:%M:%SZ')
                    })
    return users_with_active_keys
 
# Generate a report
def generate_report(data):
    report = "UserName,AccessKeyId,CreateDate\n"
    for item in data:
        report += f"{item['UserName']},{item['AccessKeyId']},{item['CreateDate']}\n"
    return report
 
if __name__ == "__main__":
    # Assume the role in the target account
    credentials = assume_role(target_account_id, role_name)
   
    # List IAM users with active access keys
    active_keys = list_iam_users_with_active_keys(credentials)
   
    report = generate_report(active_keys)
    with open('Users_active_keys_report.csv', 'w') as file:
        file.write(report)
    print("Users_keys_report.csv")