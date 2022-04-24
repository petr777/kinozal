from typing import Optional
from models.film import Film
import json

from functools import lru_cache
from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5

class FilmService:


    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    # get_by_id возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе
    async def get_by_id(self, film_id: str) -> Optional[Film]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        film = await self._film_from_cache(film_id)
        if not film:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            film = await self._get_film_from_elastic(film_id)
            if not film:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм  в кеш
            await self._put_film_to_cache(film)
        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get('movies', film_id)
        except Exception as err:
            return None
        return Film(**doc['_source'])

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        # Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get
        data = await self.redis.get(film_id)
        if not data:
            return None
        # pydantic предоставляет удобное API для создания объекта моделей из json
        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        # Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set
        # pydantic позволяет сериализовать модель в json
        await self.redis.set(film.id, film.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS)

    search_fields: list = [
        'actors_names',
        'writers_names',
        'title',
        'description',
        'genre'
    ]

    max_docs: int = 250
    limit: int = 25

    async def get_many_films(self, query_films):
        hash_query = hash(frozenset(query_films.dict().items()))
        data = await self._films_from_cache(hash_query)
        if not data:
            data = await self._get_many_film_from_elastic(query_films)
            if not data:
                return None
            await self._put_many_film_to_cache(hash_query, data)
        print(data)
        return data


    async def _get_many_film_from_elastic(self, query_films):

        es_query = dict()
        es_query['size'] = self.max_docs

        # Смотрим есть ли запрос, то формируем корректный запрос для ES
        if query_films.query:
            es_query['query'] = get_query(
                fields=self.search_fields,
                query=query_films.query
            )

        # Смотрим нужна ли сортировка, и по какому полю
        # по которому буду сортироваться данные
        if query_films.sort:
            es_query['sort'] = [get_sort(query_films.sort)]

        # Получаем все данные
        result = await self.elastic.search(index='movies', body=es_query)
        total = result['hits']['total']['value']

        # TODO paginator
        films, curent_page = get_data_page(
            total, result, query_films.page, self.limit
        )
        return total, curent_page, films


    async def _films_from_cache(self, hash_query: hash) -> Optional[Film]:

        data = await self.redis.get(hash_query)
        if not data:
            return None
        film = Film.parse_raw(data)
        return film


    async def _put_many_film_to_cache(self, hash_query: hash, films):
        data = json.dumps(films)
        await self.redis.set(hash_query, data, expire=FILM_CACHE_EXPIRE_IN_SECONDS)

def get_sort(field: str):
    sort_params = {
        'rating': {
            'imdb_rating': {"numeric_type": "double", "order": "desc"}

        },
        "title": {"title.raw": {"order": "desc"}}
    }
    return sort_params.get(field)

def get_query(fields: list, query):
    return {
        'multi_match': {
            'query': query,
            'fields': fields
        }
    }

def get_data_page(total, result, num_page, limit):
    data = [
        doc['_source']
        for doc in result['hits']['hits']
    ]

    if limit * num_page > total or num_page == 0:
        data = data[:limit]
        num_page = 1
        return data, num_page

    size = limit * num_page - 1
    return data[size:], num_page



@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic)
) -> FilmService:
    return FilmService(redis, elastic)


