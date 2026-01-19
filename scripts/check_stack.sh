#!/bin/bash

# 全てのアクティブなスタック名を取得
stacks=$(aws cloudformation list-stacks \
    --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE ROLLBACK_COMPLETE \
    --query "StackSummaries[].StackName" \
    --output text)

echo "--------------------------------------------------------------------------------"
echo "🔍  CloudFormation Stack Outputs Explorer"
echo "--------------------------------------------------------------------------------"

for stack in $stacks; do
    # 各スタックの Outputs を取得
    outputs=$(aws cloudformation describe-stacks \
        --stack-name "$stack" \
        --query "Stacks[0].Outputs" \
        --output table)

    # Outputs が存在する場合のみ表示
    if [[ "$outputs" != "None" ]]; then
        echo ""
        echo "📂 Stack: $stack"
        # Cognito関連のキーワードが含まれる場合に色を付ける (OSX/Linux両対応)
        if echo "$stack" | grep -iqE "auth|cognito|user|idp"; then
            echo -e "\033[1;33m⭐ このスタックは認証に関連している可能性があります\033[0m"
        fi
        echo "$outputs"
    fi
done

echo "--------------------------------------------------------------------------------"
echo "✅  探索完了"
