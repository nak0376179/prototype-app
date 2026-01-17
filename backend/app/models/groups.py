from pydantic import BaseModel, Field


class Group(BaseModel):
    groupid: str = Field(..., description="グループID")
    groupname: str = Field(..., description="グループ名")
    description: str | None = Field(None, description="グループの説明")


class GroupCreate(BaseModel):
    groupid: str = Field(..., description="グループID")
    groupname: str = Field(..., description="グループ名")
    description: str | None = Field(None, description="グループの説明")


class GroupUpdate(BaseModel):
    groupname: str | None = Field(None, description="変更後のグループ名")
    description: str | None = Field(None, description="変更後のグループの説明")
