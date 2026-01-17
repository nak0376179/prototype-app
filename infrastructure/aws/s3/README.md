# samplefastapi-dynamodb-stack

このスタックは、FastAPI アプリケーションで使用する以下の DynamoDB テーブルを AWS SAM を使って構築するためのものです。  
すべてのテーブルは **プロビジョンドモード（RCU/WCU = 1）** で作成されます。

---

## 📦 作成される DynamoDB テーブル

### 👤 `samplefastapi-users-{Stage}`

- **主キー**: `userid (HASH)`
- **用途**: ユーザー情報の保存

---

### 👥 `samplefastapi-groups-{Stage}`

- **主キー**: `groupid (HASH)`
- **用途**: グループ情報の保存

---

### 📝 `samplefastapi-logs-{Stage}`

- **主キー**:

  - `groupid (HASH)`
  - `created_at (RANGE)`

- **用途**: グループ内のアクティビティログの保存

- **グローバルセカンダリインデックス（GSI）**:
  - `groupid-type-created_at-index`
    - パーティションキー: `groupid#type`
    - ソートキー: `created_at`
  - `groupid-userid-created_at-index`
    - パーティションキー: `groupid#userid`
    - ソートキー: `created_at`

---

## 🚀 デプロイ手順

以下のコマンドでデプロイしてください：

```bash
sam deploy \
  --stack-name samplefastapi-dynamodb-stack-dev \
  --parameter-overrides Stage=dev \
  --capabilities CAPABILITY_IAM
```
