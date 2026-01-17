# FastAPI Cognito Stack

このスタックは、FastAPI アプリケーションのための **Cognito UserPool** を構築します。

---

## 構成概要

- `Cognito UserPool`
  - ログイン ID はメールアドレス
  - 属性に `name`, `phone_number` を含む
  - サインアップは不可（管理者作成のみ）
- `UserPoolClient`
  - `USER_PASSWORD_AUTH` などのログインフローを許可

---

## デプロイ方法（例）

```bash
sam deploy \
  --stack-name fastapi-dev-cognito-stack \
  --parameter-overrides Stage=dev \
  --capabilities CAPABILITY_IAM
```

---

## 出力内容

- `UserPoolId`
- `UserPoolClientId`

---

## テストアカウント登録

下記の Python スクリプトを使って、Cognito にテストアカウントを登録できます：

```bash
python register_test_user.py \
  --user-pool-id <UserPoolId> \
  --email test@example.com \
  --password Passw0rd! \
  --name テストユーザー \
  --phone +819012345678
```
