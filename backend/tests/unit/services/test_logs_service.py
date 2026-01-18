from typing import Any


def test_list_logs_by_groupid_excludes_others(logs_service: Any, mock_logs_repo: Any, sample_logs: Any) -> None:
    """
    指定したgroupidに一致するログのみを取得できることを検証する。

    前提:
        - group-A と group-B にそれぞれ100件のログが存在。
    実行:
        - groupid="group-A" を指定して list_logs を呼び出す。
    期待結果:
        - 返却されるログの groupid がすべて "group-A"。
        - group-B のデータは含まれない。
    """
    mock_logs_repo.list_logs.return_value = {"Items": sample_logs["group-A"]}
    result = logs_service.list_logs(groupid="group-A")
    assert all(item["groupid"] == "group-A" for item in result["Items"])
    mock_logs_repo.list_logs.assert_called_once_with(
        groupid="group-A",
        userid=None,
        type_=None,
        begin=None,
        end=None,
        limit=25,  # デフォルトの25件を指定
        startkey=None,
    )


def test_list_logs_by_userid(logs_service: Any, mock_logs_repo: Any, sample_logs: Any) -> None:
    """
    useridでフィルタリングされたログが返されることを確認する。
    """
    target_user = sample_logs["group-A"][0]["userid"]
    filtered = [item for item in sample_logs["group-A"] if item["userid"] == target_user]
    mock_logs_repo.list_logs.return_value = {"Items": filtered}

    result = logs_service.list_logs(groupid="group-A", userid=target_user)
    assert all(item["userid"] == target_user for item in result["Items"])


def test_list_logs_by_type(logs_service: Any, mock_logs_repo: Any, sample_logs: Any) -> None:
    """
    typeでフィルタリングされたログが返されることを確認する。
    """
    target_type = "Login"
    filtered = [item for item in sample_logs["group-A"] if item["type"] == target_type]
    mock_logs_repo.list_logs.return_value = {"Items": filtered}

    result = logs_service.list_logs(groupid="group-A", type_=target_type)
    assert all(item["type"] == target_type for item in result["Items"])


def test_list_logs_with_time_range(logs_service: Any, mock_logs_repo: Any, sample_logs: Any) -> None:
    """
    指定した期間内のログのみが返されることを確認する。
    """
    begin = "2024-01-01T00:00:01Z"
    end = "2024-01-01T00:00:03Z"
    filtered = [item for item in sample_logs["group-A"] if begin <= item["created_at"] <= end]
    mock_logs_repo.list_logs.return_value = {"Items": filtered}

    result = logs_service.list_logs(groupid="group-A", begin=begin, end=end)
    assert all(begin <= item["created_at"] <= end for item in result["Items"])


def test_list_logs_with_limit_100(logs_service: Any, mock_logs_repo: Any, sample_logs: Any) -> None:
    """
    100件のデータがあった場合、limit=100を指定してすべてのログが取得されることを確認する。
    """
    mock_logs_repo.list_logs.return_value = {"Items": sample_logs["group-A"]}

    result = logs_service.list_logs(groupid="group-A", limit=100)
    assert len(result["Items"]) == 100  # 100件のデータが返されること
    assert all(item["groupid"] == "group-A" for item in result["Items"])


def test_list_logs_with_pagination(logs_service: Any, mock_logs_repo: Any, sample_logs: Any) -> None:
    """
    ページネーションが有効で、startkey によって次のページが取得されることを確認する。
    """
    page1 = {"Items": sample_logs["group-A"][:25], "LastEvaluatedKey": {"created_at": "2024-01-01T00:00:02Z"}}
    page2 = {"Items": sample_logs["group-A"][25:50]}

    # 1ページ目
    mock_logs_repo.list_logs.return_value = page1
    result1 = logs_service.list_logs(groupid="group-A", limit=25)
    assert "LastEvaluatedKey" in result1
    assert len(result1["Items"]) == 25

    # 2ページ目
    mock_logs_repo.list_logs.return_value = page2
    result2 = logs_service.list_logs(groupid="group-A", limit=25, startkey=page1["LastEvaluatedKey"])
    assert len(result2["Items"]) == 25


def test_list_logs_with_pagination_has_next(logs_service: Any, mock_logs_repo: Any, sample_logs: Any) -> None:
    """
    次のページが存在する場合、LastEvaluatedKeyが返されることを確認する。
    """
    page1 = {"Items": sample_logs["group-A"][:25], "LastEvaluatedKey": {"created_at": "2024-01-01T00:00:02Z"}}

    # 1ページ目
    mock_logs_repo.list_logs.return_value = page1
    result1 = logs_service.list_logs(groupid="group-A", limit=25)
    assert "LastEvaluatedKey" in result1
    assert len(result1["Items"]) == 25


def test_list_logs_with_limit_more_than_total(logs_service: Any, mock_logs_repo: Any, sample_logs: Any) -> None:
    """
    limitが総件数より大きい場合、全件が返されることを確認する。
    """
    mock_logs_repo.list_logs.return_value = {"Items": sample_logs["group-A"]}

    result = logs_service.list_logs(groupid="group-A", limit=200)
    assert len(result["Items"]) == 100  #
