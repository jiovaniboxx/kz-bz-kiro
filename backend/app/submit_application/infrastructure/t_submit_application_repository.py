import boto3
from botocore.exceptions import ClientError
from submit_application.infrastructure.dynamodb import DynamodbOperations

TABLE_NAME = 't_submit_application'
dynamo_client = boto3.client('dynamodb')

def t_submit_application_repository_save(submit_application):
    try:
        options = {
            'TableName': TABLE_NAME,
            'Item': {
                'name': {'S': submit_application.name},
                'email': {'S': submit_application.email},
                'message': {'S': submit_application.message},
                'created_at': {'S': submit_application.created_at.isoformat()},
            },
        }
        dynamo_operations = DynamodbOperations(TABLE_NAME)
        dynamo_operations.put_item(options)
    except ClientError as e:
        print(f"Error saving submit_application: {e.response['Error']['Message']}")
        return False
