## テーブルができているか確認したい。

```
aws dynamodb list-tables --endpoint-url http://localhost:4566

aws dynamodb scan --table-name samplefastapi-users-devel --endpoint-url http://localhost:4566 | jq -c '.Items[]'
aws dynamodb scan --table-name samplefastapi-groups-devel --endpoint-url http://localhost:4566 | jq -c '.Items[]'
```

## コンテナに入ってテーブルができているか確認したい。

```
docker exec -it localstack bash
awslocal dynamodb list-tables
```
