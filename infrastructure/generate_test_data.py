import json
import random
import argparse
from datetime import datetime, timedelta

# 定数
NUM_GROUPS = 10
NUM_USERS = 30
NUM_LOGS = 200
GROUP_PREFIX = "group"
USER_PREFIX = "user"

# CLI引数の処理
parser = argparse.ArgumentParser()
parser.add_argument(
    "--appname", required=True, help="アプリケーション名 (例: samplefastapi)"
)
parser.add_argument(
    "--env", required=True, choices=["devel", "staging", "prod"], help="環境名"
)
args = parser.parse_args()
appname = args.appname
env = args.env

group_ids = [f"{GROUP_PREFIX}{i + 1}" for i in range(NUM_GROUPS)]
user_emails = [f"{USER_PREFIX}{i + 1}@example.com" for i in range(NUM_USERS)]
user_names = [
    "Alice",
    "Bob",
    "Charlie",
    "Dave",
    "Eve",
    "Frank",
    "Grace",
    "Heidi",
    "Ivan",
    "Judy",
]

# グループとユーザーの対応を作成
group_to_users: dict[str, list[dict[str, str]]] = {gid: [] for gid in group_ids}
user_to_groups: dict[str, list[str]] = {}

users: list[dict[str, dict[str, str | list]]] = []
groups: list[dict[str, dict[str, str | list]]] = []
logs: list[dict[str, dict[str, str | list]]] = []

for email in user_emails:
    name = random.choice(user_names)
    n = random.randint(1, 5)
    assigned_groups = random.sample(group_ids, n)

    groups_list = []
    for gid in assigned_groups:
        role = random.choice(["admin", "member", "guest"])
        groups_list.append({"M": {"groupid": {"S": gid}, "role": {"S": role}}})
        group_to_users[gid].append({"email": email, "role": role})

    user_to_groups[email] = assigned_groups

    users.append(
        {
            "userid": {"S": email},
            "email": {"S": email},
            "username": {"S": name},
            "groups": {"L": groups_list},
        }
    )

    group_roles = ", ".join(
        f"{g['groupid']['S']}({g['role']['S']})"
        for g in [item["M"] for item in groups_list]
    )
    print(f"✅ ユーザーを追加しました: {name} ({email}) 所属グループ: {group_roles}")

# グループを生成
for gid in group_ids:
    users_list = [
        {"M": {"userid": {"S": u["email"]}, "role": {"S": u["role"]}}}
        for u in group_to_users[gid]
    ]

    groups.append(
        {
            "groupid": {"S": gid},
            "groupname": {"S": f"グループ {gid[len(GROUP_PREFIX) :]}"},
            "users": {"L": users_list},
        }
    )

# ログを生成
log_types = ["LOGIN", "LOGOUT", "CREATE", "DELETE"]
start_time = datetime(2025, 5, 1, 8, 0, 0)

unique_keys = set()

for _ in range(NUM_LOGS):
    group_id = random.choice(group_ids)
    if group_to_users[group_id]:
        user = random.choice(group_to_users[group_id])
        user_email = user["email"]
    else:
        user_email = random.choice(user_emails)

    user_name = next(
        u["username"]["S"] for u in users if u["userid"]["S"] == user_email
    )

    log_type = random.choice(log_types)
    timestamp = start_time + timedelta(minutes=random.randint(0, 1440))
    created_at = timestamp.isoformat() + "Z"

    key = (group_id, user_email, created_at)
    if key in unique_keys:
        continue  # skip duplicates
    unique_keys.add(key)

    logs.append(
        {
            "groupid": {"S": group_id},
            "created_at": {"S": created_at},
            "userid": {"S": user_email},
            "username": {"S": user_name},
            "type": {"S": log_type},
            "message": {"S": f"{user_name} が {log_type.lower()} しました"},
            "groupid#type": {"S": f"{group_id}#{log_type}"},
            "groupid#userid": {"S": f"{group_id}#{user_email}"},
        }
    )


# ファイル出力関数
def write_jsonl(table_name, items):
    filename = f"{appname}-{table_name}-{env}.jsonl"
    with open(filename, "w", encoding="utf-8") as f:
        for item in items:
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")
    print(f"📄 {filename} に {len(items)} 件を書き出しました。")


# JSONL として保存
write_jsonl("users", users)
write_jsonl("groups", groups)
write_jsonl("logs", logs)
