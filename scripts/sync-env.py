#!/usr/bin/env python3
"""
環境変数同期スクリプト

ルートの.envファイルからfrontend/.envとbackend samconfig.tomlを生成します。
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any


class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


def load_env_file(env_path: Path) -> dict[str, str]:
    """環境変数ファイルを読み込む"""
    env_vars = {}
    if not env_path.exists():
        return env_vars

    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()

    return env_vars


def update_frontend_env(env_vars: dict[str, str], env: str) -> None:
    """Frontend .envファイルを更新"""
    frontend_env_path = Path("frontend/.env")

    # 環境に応じたCognito設定を取得
    user_pool_id = env_vars.get(f"COGNITO_USER_POOL_ID_{env.upper()}", "")
    client_id = env_vars.get(f"COGNITO_CLIENT_ID_{env.upper()}", "")
    demo_user_pool_id = env_vars.get("DEMO_USER_POOL_ID", "")
    demo_client_id = env_vars.get("DEMO_CLIENT_ID", "")

    # API URLを取得
    if env == "devel":
        api_url = env_vars.get("API_URL_LOCAL", "http://localhost:8000")
    else:
        api_url = env_vars.get(f"API_URL_{env.upper()}", "")

    region = env_vars.get("AWS_REGION", "ap-northeast-1")

    # Frontend .envの内容を生成
    content = f"""#VITE_API_URL=https://your-api-gateway-url.execute-api.{region}.amazonaws.com/v1
VITE_API_URL={api_url}
#VITE_API_URL=http://localhost:3000
VITE_REGION={region}
VITE_USER_POOL_ID={user_pool_id}
VITE_USER_POOL_WEB_CLIENT_ID={client_id}
VITE_DEMO_USER_POOL_ID={demo_user_pool_id}
VITE_DEMO_USER_POOL_WEB_CLIENT_ID={demo_client_id}
"""

    # ファイルに書き込み
    with open(frontend_env_path, "w") as f:
        f.write(content)

    print(f"{Colors.GREEN}✓{Colors.END} Frontend .env updated for {Colors.BOLD}{env}{Colors.END} environment")
    print(f"  - User Pool ID: {Colors.BLUE}{user_pool_id}{Colors.END}")
    print(f"  - API URL: {Colors.BLUE}{api_url}{Colors.END}")


def update_samconfig(env_vars: dict[str, str]) -> None:
    """Backend samconfig.tomlを更新"""
    samconfig_path = Path("infrastructure/aws/backend/samconfig.toml")

    if not samconfig_path.exists():
        print(f"{Colors.RED}✗{Colors.END} samconfig.toml not found")
        return

    # samconfig.tomlを読み込む
    with open(samconfig_path) as f:
        content = f.read()

    # 各環境のUser Pool IDを置換
    for env in ["devel", "staging", "prod"]:
        user_pool_id = env_vars.get(f"COGNITO_USER_POOL_ID_{env.upper()}", f"{env.upper()}_USER_POOL_ID")

        # プレースホルダーまたは既存の値を置換
        pattern = f'(parameter_overrides = ".*CognitoUserPoolId=)([^"]+)(")'

        def replace_for_env(match: Any) -> str:
            line = match.group(0)
            # 該当する環境のセクション内かチェック
            if f"Env={env}" in line:
                return f"{match.group(1)}{user_pool_id}{match.group(3)}"
            return match.group(0)

        # 環境ごとのセクションを探して置換
        env_section_pattern = f"\\[{env}\\.deploy\\.parameters\\]([^\\[]*)"

        def replace_section(match: Any) -> str:
            section = match.group(0)
            section = re.sub(
                f'(parameter_overrides = ".*CognitoUserPoolId=)([^"]+)(")',
                f"\\g<1>{user_pool_id}\\g<3>",
                section,
            )
            return section

        content = re.sub(env_section_pattern, replace_section, content, flags=re.DOTALL)

    # ファイルに書き込み
    with open(samconfig_path, "w") as f:
        f.write(content)

    print(f"{Colors.GREEN}✓{Colors.END} Backend samconfig.toml updated")
    for env in ["devel", "staging", "prod"]:
        user_pool_id = env_vars.get(f"COGNITO_USER_POOL_ID_{env.upper()}", f"{env.upper()}_USER_POOL_ID")
        print(f"  - {env}: {Colors.BLUE}{user_pool_id}{Colors.END}")


def main() -> None:
    parser = argparse.ArgumentParser(description="環境変数をfrontend/backendに同期します")
    parser.add_argument(
        "--env",
        default="devel",
        choices=["devel", "staging", "prod"],
        help="Frontend環境 (デフォルト: devel)",
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        help=".envファイルのパス (デフォルト: .env)",
    )

    args = parser.parse_args()

    # プロジェクトルートに移動
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)

    # .envファイルを読み込み
    env_path = Path(args.env_file)
    if not env_path.exists():
        print(f"{Colors.RED}✗{Colors.END} {args.env_file} not found")
        print(f"{Colors.YELLOW}ℹ{Colors.END}  Copy .env.example to .env and set your values")
        sys.exit(1)

    print(f"{Colors.BOLD}{Colors.BLUE}Loading environment variables from {args.env_file}...{Colors.END}\n")
    env_vars = load_env_file(env_path)

    if not env_vars:
        print(f"{Colors.RED}✗{Colors.END} No environment variables found in {args.env_file}")
        sys.exit(1)

    # Frontend .envを更新
    update_frontend_env(env_vars, args.env)
    print()

    # Backend samconfig.tomlを更新
    update_samconfig(env_vars)
    print()

    print(f"{Colors.GREEN}{Colors.BOLD}✓ Synchronization complete!{Colors.END}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")
        sys.exit(1)
