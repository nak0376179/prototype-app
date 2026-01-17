from typing import Annotated, Any

from pydantic import BaseModel, EmailStr, Field, StringConstraints


class User(BaseModel):
    userid: str = Field(..., description="ユーザーID")
    username: Annotated[str, StringConstraints(max_length=30)] = Field(..., description="ユーザー名")
    email: EmailStr = Field(..., description="メールアドレス")


class UserCreate(BaseModel):
    userid: str = Field(..., description="ユーザーID")
    username: Annotated[str, StringConstraints(max_length=30)] = Field(..., description="ユーザー名")
    email: EmailStr = Field(..., description="メールアドレス")


class UserUpdate(BaseModel):
    username: Annotated[str, StringConstraints(max_length=30)] | None = Field(default=None, description="変更後のユーザー名")
    email: EmailStr | None = Field(default=None, description="変更後のメールアドレス")


class UsersResponse(BaseModel):
    Items: list[User] = Field(..., description="ユーザー情報の一覧（IDと名前）")
    LastEvaluatedKey: dict[str, Any] | None = Field(default=None, description="次ページ取得用の開始キー。これが存在する場合はさらにデータがあります。")


class UserBrief(BaseModel):
    userid: str = Field(..., description="ユーザーID")
    username: Annotated[str, StringConstraints(max_length=30)] = Field(..., description="ユーザー名")


class UsersBriefResponse(BaseModel):
    Items: list[UserBrief] = Field(..., description="ユーザー情報の一覧（IDと名前）")


class MessageResponse(BaseModel):
    message: str
