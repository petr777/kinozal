from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict
from services.film import FilmService, get_film_service
from models.schema_film import FullFilm, QueryFilms, ShortFilm


router = APIRouter()

@router.get('/{film_id}', response_model=FullFilm)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> FullFilm:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
    return FullFilm(**film.dict())


@router.get('/', response_model=Dict)
async def films(
        film_service: FilmService = Depends(get_film_service),
        query_films: QueryFilms = Depends()
):

    total, curent_page, films = await film_service.get_many_films(query_films)

    return {
        'total': total,
        'page': curent_page,
        'result': [ShortFilm(**film) for film in films],
    }
