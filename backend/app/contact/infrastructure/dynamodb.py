import boto3
from botocore.config import Config
import datetime
import os
from datetime import timezone

AWS_REGION = os.environ.get('AWS_REGION')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
DYNAMO_ENDPOINT = os.environ.get('DYNAMO_ENDPOINT')

class DynamodbOperations:
    def __init__(self, table_name):
        if AWS_ACCESS_KEY_ID is not None and AWS_SECRET_ACCESS_KEY is not None:
            self.TABLE_NAME = table_name
            self.dynamo_client = boto3.client(
                'dynamodb',
                region_name=AWS_REGION,  # リージョンを明示的に指定
                config=Config(retries={'max_attempts': 10}),
                endpoint_url=DYNAMO_ENDPOINT,  # LocalStackのエンドポイント
                aws_access_key_id=AWS_ACCESS_KEY_ID,  # ダミーのアクセスキー
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY  # ダミーのシークレットキー
            )
        else:
            self.TABLE_NAME = table_name
            self.dynamo_client = boto3.client(
                'dynamodb',
                region_name=AWS_REGION,  # リージョンを明示的に指定
                config=Config(retries={'max_attempts': 10}),
            )

    def scan(self, options: dict):
        ret = []
        while True:
            res = self.dynamo_client.scan(**options)
            ret += res.get('Items', [])
            if 'LastEvaluatedKey' not in res:
                break
            options['ExclusiveStartKey'] = res['LastEvaluatedKey']

        print(len(ret))
        print(ret)

    def put_item(self, options: dict):
        # now = int(datetime.now(timezone.utc).timestamp() * 1000)
        ret = self.dynamo_client.put_item(**options)
        return ret

    def get_item(self, options: dict):
        ret = self.dynamo_client.get_item(**options)
        return ret

    def update_item(self, options: dict):
        now = int(datetime.now(timezone.utc).timestamp() * 1000)
        ret = self.dynamo_client.update_item(**options)
        return ret


    def delete_item(self, options: dict):
        ret = self.dynamo_client.delete_item(**options)
        return ret