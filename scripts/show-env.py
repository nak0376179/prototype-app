#!/usr/bin/env python3
"""
prototype-app 開発環境確認スクリプト

AWS上にデプロイされているprototype-app関連のリソース（CloudFormation、DynamoDB）を確認します。
"""

import argparse
import json
import subprocess
import sys
from typing import Any


class Colors:
    """ターミナル出力用のカラーコード"""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def print_header(text: str) -> None:
    """ヘッダーを表示"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}\n")


def print_section(text: str) -> None:
    """セクションタイトルを表示"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BLUE}{'-' * 80}{Colors.END}")


def print_key_value(key: str, value: str, indent: int = 2) -> None:
    """キーと値を整形して表示"""
    spaces = " " * indent
    # prototype-app を強調表示
    if "prototype-app" in value:
        value = value.replace("prototype-app", f"{Colors.BOLD}{Colors.GREEN}prototype-app{Colors.END}")
    print(f"{spaces}{Colors.YELLOW}{key}:{Colors.END} {value}")


def print_warning(text: str) -> None:
    """警告メッセージを表示"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_error(text: str) -> None:
    """エラーメッセージを表示"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_success(text: str) -> None:
    """成功メッセージを表示"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def run_aws_command(command: list[str]) -> dict[str, Any] | None:
    """AWS CLIコマンドを実行して結果を返す"""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )
        if result.stdout.strip():
            return json.loads(result.stdout)
        return None
    except subprocess.CalledProcessError:
        return None
    except json.JSONDecodeError:
        return None


def check_lambda_layer_stack(env: str, region: str) -> None:
    """Lambda Layerスタックの情報を表示"""
    print_section(f"🔧 Lambda Layer Stack: prototype-app-lambda-layer-stack-{env}")

    stack_name = f"prototype-app-lambda-layer-stack-{env}"
    result = run_aws_command(
        [
            "aws",
            "cloudformation",
            "describe-stacks",
            "--stack-name",
            stack_name,
            "--region",
            region,
            "--query",
            "Stacks[0].{Status:StackStatus,Outputs:Outputs}",
        ]
    )

    if not result:
        print_warning("Stack not deployed yet")
        return

    status = result.get("Status", "UNKNOWN")
    status_color = Colors.GREEN if "COMPLETE" in status else Colors.YELLOW
    print_key_value("Status", f"{status_color}{status}{Colors.END}")

    outputs = result.get("Outputs", [])
    if outputs:
        print(f"\n  {Colors.CYAN}Outputs:{Colors.END}")
        for output in outputs:
            key = output.get("OutputKey", "")
            value = output.get("OutputValue", "")
            print_key_value(f"  {key}", value, indent=4)


def check_backend_stack(env: str, region: str) -> None:
    """Backendスタックの情報を表示"""
    print_section(f"🚀 Backend Stack: prototype-app-backend-stack-{env}")

    stack_name = f"prototype-app-backend-stack-{env}"
    result = run_aws_command(
        [
            "aws",
            "cloudformation",
            "describe-stacks",
            "--stack-name",
            stack_name,
            "--region",
            region,
            "--query",
            "Stacks[0].{Status:StackStatus,Parameters:Parameters,Outputs:Outputs}",
        ]
    )

    if not result:
        print_warning("Stack not deployed yet")
        return

    # ステータス表示
    status = result.get("Status", "UNKNOWN")
    status_color = Colors.GREEN if "COMPLETE" in status else Colors.YELLOW
    print_key_value("Status", f"{status_color}{status}{Colors.END}")

    # パラメータ表示
    parameters = result.get("Parameters", [])
    if parameters:
        print(f"\n  {Colors.CYAN}Parameters:{Colors.END}")
        for param in parameters:
            key = param.get("ParameterKey", "")
            value = param.get("ParameterValue", "")
            print_key_value(f"  {key}", value, indent=4)

    # Outputs表示
    outputs = result.get("Outputs", [])
    if outputs:
        print(f"\n  {Colors.CYAN}Outputs:{Colors.END}")
        for output in outputs:
            key = output.get("OutputKey", "")
            value = output.get("OutputValue", "")
            print_key_value(f"  {key}", value, indent=4)


def check_dynamodb_tables(env: str, region: str) -> None:
    """DynamoDBテーブルの情報を表示"""
    print_section("🗄️  DynamoDB Tables")

    tables = [
        f"prototype-app-users-{env}",
        f"prototype-app-groups-{env}",
        f"prototype-app-logs-{env}",
    ]

    for table_name in tables:
        # テーブル情報を取得
        table_info = run_aws_command(
            [
                "aws",
                "dynamodb",
                "describe-table",
                "--table-name",
                table_name,
                "--region",
                region,
                "--query",
                "Table.{TableStatus:TableStatus,ItemCount:ItemCount}",
            ]
        )

        if not table_info:
            print_error(f"{table_name}: Not found")
            continue

        # アイテム数を取得
        count_result = run_aws_command(
            [
                "aws",
                "dynamodb",
                "scan",
                "--table-name",
                table_name,
                "--region",
                region,
                "--select",
                "COUNT",
                "--query",
                "Count",
            ]
        )

        status = table_info.get("TableStatus", "UNKNOWN")
        count = count_result if count_result is not None else 0

        # 強調表示されたテーブル名
        display_name = table_name.replace("prototype-app", f"{Colors.BOLD}{Colors.GREEN}prototype-app{Colors.END}")

        status_color = Colors.GREEN if status == "ACTIVE" else Colors.YELLOW
        print(f"  {Colors.GREEN}✓{Colors.END}  {display_name}: {status_color}{status}{Colors.END} ({count} items)")


def check_cognito(env: str, region: str) -> None:
    """Cognito User Poolの情報を表示"""
    print_section("🔐 Cognito User Pool")

    stack_name = f"prototype-app-backend-stack-{env}"

    # Backendスタックからパラメータを取得
    result = run_aws_command(
        [
            "aws",
            "cloudformation",
            "describe-stacks",
            "--stack-name",
            stack_name,
            "--region",
            region,
            "--query",
            "Stacks[0].Parameters[?ParameterKey==`CognitoUserPoolId`].ParameterValue",
            "--output",
            "text",
        ]
    )

    if not result:
        print_warning("Cognito User Pool ID not found in stack parameters")
        return

    # User Pool IDを取得（リストではなく文字列として）
    user_pool_id = result if isinstance(result, str) else None
    if not user_pool_id:
        print_warning("Cognito User Pool ID not found")
        return

    # User Pool詳細を取得
    pool_info = run_aws_command(
        [
            "aws",
            "cognito-idp",
            "describe-user-pool",
            "--user-pool-id",
            user_pool_id,
            "--region",
            region,
            "--query",
            "UserPool.{Id:Id,Name:Name,Status:Status,CreationDate:CreationDate}",
        ]
    )

    if pool_info:
        for key, value in pool_info.items():
            print_key_value(key, str(value))
    else:
        print_error(f"User Pool {user_pool_id} not found")


def main() -> None:
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description="prototype-app AWS環境の状態を確認します",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--env",
        default="devel",
        choices=["devel", "staging", "prod"],
        help="環境名 (デフォルト: devel)",
    )
    parser.add_argument(
        "--region",
        default="ap-northeast-1",
        help="AWSリージョン (デフォルト: ap-northeast-1)",
    )
    parser.add_argument(
        "--component",
        choices=["all", "layer", "backend", "dynamodb", "cognito"],
        default="all",
        help="表示するコンポーネント (デフォルト: all)",
    )

    args = parser.parse_args()

    # ヘッダー表示（allの場合のみ）
    if args.component == "all":
        print_header(f"📊  prototype-app AWS Environment Status (ENV={args.env}, REGION={args.region})")

    # 各リソースの確認
    if args.component in ["all", "layer"]:
        check_lambda_layer_stack(args.env, args.region)

    if args.component in ["all", "backend"]:
        check_backend_stack(args.env, args.region)

    if args.component in ["all", "dynamodb"]:
        check_dynamodb_tables(args.env, args.region)

    if args.component == "cognito":
        check_cognito(args.env, args.region)

    # フッター（allの場合のみ）
    if args.component == "all":
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}中断されました{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print_error(f"エラーが発生しました: {e}")
        sys.exit(1)
