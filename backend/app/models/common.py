from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class SingleItemData:
    item: dict[str, Any]


@dataclass(frozen=True)
class ListItemData:
    items: list[dict[str, Any]] = field(default_factory=list)
    last_evaluated_key: dict[str, Any] | None = None
    size: int = 0
    count: int = 0


@dataclass(frozen=True)
class MessageData:
    message: str = "OK"


@dataclass(frozen=True)
class RepositoryResponse[T]:
    code: int
    data: T | None = None
    detail: str | None = None

    @property
    def is_success(self) -> bool:
        return 200 <= self.code < 300 or self.code == 20000


@dataclass(frozen=True)
class ServiceResponse[T]:
    code: int
    data: T | None = None
    detail: str | None = None

    @property
    def is_success(self) -> bool:
        return 200 <= self.code < 300 or self.code == 20000


@dataclass(frozen=True)
class Group:
    groupid: str
    groupname: str
    description: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class LogItem:
    groupid: str
    userid: str | None
    username: str | None
    type: str | None
    message: str | None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class User:
    userid: str
    username: str
    email: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
