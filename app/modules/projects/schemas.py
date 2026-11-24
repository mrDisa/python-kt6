from pydantic import BaseModel, ConfigDict, Field

class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None

class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None

class ProjectOut(BaseModel):
    id: int
    name: str
    description: str | None
    owner_id: int
    model_config = ConfigDict(from_attributes=True)
