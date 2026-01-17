import boto3
import argparse


def create_user(pool_id, email, password, name, phone):
    client = boto3.client("cognito-idp")

    client.admin_create_user(
        UserPoolId=pool_id,
        Username=email,
        UserAttributes=[
            {"Name": "email", "Value": email},
            {"Name": "name", "Value": name},
            {"Name": "phone_number", "Value": phone},
            {"Name": "email_verified", "Value": "true"},
        ],
        MessageAction="SUPPRESS",
    )

    client.admin_set_user_password(
        UserPoolId=pool_id, Username=email, Password=password, Permanent=True
    )

    print("✅ User created:", email)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--user-pool-id", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--phone", required=True)
    args = parser.parse_args()

    create_user(args.user_pool_id, args.email, args.password, args.name, args.phone)
