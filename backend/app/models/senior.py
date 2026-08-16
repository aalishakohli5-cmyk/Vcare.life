from pydantic import BaseModel
from typing import Optional

class SeniorCreate(BaseModel):
    name: str
    age: int
#class inheritance
class Senior(SeniorCreate):
    id: int