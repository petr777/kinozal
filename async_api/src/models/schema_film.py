from pydantic import BaseModel
from typing import Optional, List


class Person(BaseModel):
    id: str
    name: str

class FullFilm(BaseModel):
    id: str
    imdb_rating: Optional[float] = 0
    genre: Optional[List[str]] = []
    title: str
    description: Optional[str] = None
    director: List[str] = []
    actors_names: List = []
    writers_names: List = []

class ShortFilm(BaseModel):
    id: str
    imdb_rating: Optional[float] = 0
    genre: Optional[List[str]] = []
    title: str


class QueryFilms(BaseModel):
    sort: Optional[str]
    page: Optional[int]
    filters: Optional[str]
    query: Optional[str]