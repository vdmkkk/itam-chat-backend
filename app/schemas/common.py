from typing import Generic, List, TypeVar
from pydantic import BaseModel, ConfigDict, Field
from pydantic.generics import GenericModel

T = TypeVar("T")


class Page(GenericModel, Generic[T]):
    model_config = ConfigDict(from_attributes=True)

    items: List[T]
    total: int = Field(..., ge=0)
    limit: int = Field(..., ge=1)
    offset: int = Field(..., ge=0)


