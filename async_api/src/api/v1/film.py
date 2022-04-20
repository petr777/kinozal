from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List

from pydantic import BaseModel
from services.film import FilmService, get_film_service
from pydantic.fields import Field

router = APIRouter()


class Person(BaseModel):
    id: str
    name: str


class Film(BaseModel):
    id: str
    rating: Optional[float] = 0
    genre: Optional[List[str]] = []
    title: str
    description: Optional[str] = None
    director: List[str] = []
    actors_names: List = []
    writers_names: List = []


class QueryFilms(BaseModel):
    sort: Optional[str]
    page: Optional[str]
    filters: Optional[str]
    query: Optional[str]


@router.get('/{film_id}', response_model=Film)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
    return Film(**film.dict())


@router.get('/', response_model=List[Film])
async def films(
        film_service: FilmService = Depends(get_film_service),
        query_films: QueryFilms = Depends()
):
    films = await film_service.get_many(query_films)
    return [Film(**film) for film in films]
