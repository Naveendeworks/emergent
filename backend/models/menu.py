from pydantic import BaseModel, Field
from typing import List, Optional

class MenuItem(BaseModel):
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=100)
    chef: str = Field(..., min_length=1, max_length=50)
    sousChef: Optional[str] = Field(None, max_length=50)
    category: str = Field(..., min_length=1, max_length=50)
    available: bool = Field(default=True)

class MenuResponse(BaseModel):
    items: List[MenuItem]
    categories: List[str]