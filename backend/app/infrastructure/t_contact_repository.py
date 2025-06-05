import boto3
from botocore.exceptions import ClientError
from app.infrastructure.dynamodb import DynamodbOperations

TABLE_NAME = 't_contact'
dynamo_client = boto3.client('dynamodb')

def t_contact_repository_save(contact):
    try:
        options = {
            'TableName': TABLE_NAME,
            'Item': {
                'name': {'S': contact.name},
                'email': {'S': contact.email},
                'message': {'S': contact.message},
                'created_at': {'S': contact.created_at.isoformat()},
            },
        }
        dynamo_operations = DynamodbOperations(TABLE_NAME)
        dynamo_operations.put_item(options)
    except ClientError as e:
        print(f"Error saving contact: {e.response['Error']['Message']}")
        return False

# エクスポートするオブジェクトを明示的に指定
__all__ = ["save"]