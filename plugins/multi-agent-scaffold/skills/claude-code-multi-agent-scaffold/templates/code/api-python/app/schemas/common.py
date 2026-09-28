"""通用 DTO：Page / PageQuery / CamelModel。"""
from typing import Generic, List, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


def _to_camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


class CamelModel(BaseModel):
    """出参基类：后端 snake_case 字段 → 响应 camelCase。"""

    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True, from_attributes=True)


class Page(BaseModel, Generic[T]):
    """统一分页信封（规范 6.2）：items / total / page / size。"""

    items: List[T]
    total: int
    page: int
    size: int


class PageQuery(BaseModel):
    page: int = 1
    size: int = 20
