import boto3
import argparse

# SNS クライアントを作成
sns_client = boto3.client("sns", region_name="ap-northeast-1")


# SNS トピックを作成する関数
def create_sns_topic(app_name, environment):
    topic_name = f"{app_name}-demo-signup-topic-{environment}"
    response = sns_client.create_topic(Name=topic_name)
    topic_arn = response["TopicArn"]
    print(f"Topic ARN: {topic_arn}")
    return topic_arn


# 購読者を SNS トピックに追加する関数
def subscribe_to_topic(topic_arn, email_address):
    subscription_response = sns_client.subscribe(
        TopicArn=topic_arn, Protocol="email", Endpoint=email_address
    )
    print(f"Subscription ARN: {subscription_response['SubscriptionArn']}")
    print("購読確認メールが送信されました。確認して購読を有効化してください。")


# 購読確認状態をチェックする関数
def check_subscription_status(subscription_arn):
    try:
        response = sns_client.get_subscription_attributes(
            SubscriptionArn=subscription_arn
        )
        subscription_status = response["Attributes"]["ConfirmationStatus"]

        if subscription_status == "Confirmed":
            print("購読確認が完了しました。")
            return True
        else:
            print("購読確認が完了していません。")
            return False
    except Exception as e:
        print(f"購読確認エラー: {e}")
        return False


# 引数を解析する関数
def parse_args():
    parser = argparse.ArgumentParser(
        description="SNSトピックを作成し、購読者を追加します。"
    )
    parser.add_argument("app_name", help="アプリ名")
    parser.add_argument("environment", help="環境 (例: dev, prod)")
    parser.add_argument("email", help="購読者のメールアドレス")
    return parser.parse_args()


# メイン処理
def main():
    # 引数を解析
    args = parse_args()

    # SNS トピックを作成
    print(f"アプリ名: {args.app_name}, 環境: {args.environment}")
    topic_arn = create_sns_topic(args.app_name, args.environment)

    # 購読者をトピックに追加
    subscribe_to_topic(topic_arn, args.email)

    # 購読確認を手動で行ってもらう
    print("購読確認を手動で行ってください。確認したら 'y' を押してください。")
    while True:
        user_input = (
            input("購読確認が完了したら 'y' を押してください: ").strip().lower()
        )
        if user_input == "y":
            break
        else:
            print("無効な入力です。'y' を押してください。")

    # 購読確認をチェック
    print("購読確認の状態をチェックしています...")
    subscription_status = check_subscription_status(
        f"arn:aws:sns:ap-northeast-1:123456789012:demo-signup-topic-dev:{topic_arn.split(':')[-1]}"
    )

    # 購読確認が完了していれば、情報を表示
    if subscription_status:
        print(f"トピック ARN: {topic_arn}")
        print(f"購読者 {args.email} が正常に購読されました。")
    else:
        print(f"購読者 {args.email} は購読確認が完了していません。")


if __name__ == "__main__":
    main()
