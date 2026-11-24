from pydantic import BaseModel, ConfigDict, Field

class TodoCreate(BaseModel):
    project_id: int
    title: str = Field(min_length=1, max_length=150)
    description: str | None = None

class TodoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    is_done: bool | None = None

class TodoOut(BaseModel):
    id: int
    project_id: int
    creator_id: int
    title: str
    description: str | None
    is_done: bool
    model_config = ConfigDict(from_attributes=True)
