#!/bin/bash
T_CONTACT='t_contact'

aws dynamodb list-tables \
--endpoint-url http://localhost:4566 \
--region ap-northeast-1 \
| grep $T_CONTACT

if [ $? -eq 0 ]; then
    aws dynamodb put-item \
    --table-name $T_CONTACT \
    --item '{ "name": { "S": "サンプル 太郎" }, "email": { "S": "sample@sample.com" }, "message": { "S": "sample message." }, "created_at": { "S": "2025-04-05T12:12:12Z" } }' \
    --endpoint-url http://localhost:4566 \
    --region ap-northeast-1
    echo "Table $T_CONTACT already exists."
else
    aws dynamodb create-table \
    --table-name $T_CONTACT \
    --attribute-definitions '[{"AttributeName":"created_at","AttributeType": "S"}]' \
    --key-schema '[{"AttributeName":"created_at","KeyType": "HASH"}]' \
    --provisioned-throughput '{"ReadCapacityUnits": 5,"WriteCapacityUnits": 5}' \
    --endpoint-url http://localhost:4566 \
    --region ap-northeast-1
fi
