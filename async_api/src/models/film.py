import orjson
from pydantic import BaseModel
from typing import Optional, List
from pydantic.fields import Field


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()

class Person(BaseModel):
    id: str
    name: str

class Film(BaseModel):
    id: str
    imdb_rating: Optional[float] = 0
    genre: Optional[List[str]] = []
    title: str
    description: Optional[str] = None
    director: List[str] = []
    actors: List[Person]
    actors_names: List = []
    writers: List[Person] = []
    writers_names: List = []


    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps