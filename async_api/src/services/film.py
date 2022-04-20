from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут



def get_sort(field: str):
    sort_params = {
        'imdb_rating': {"numeric_type": "double"},
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




class FilmService:

    search_fields: list = [
        'actors_names',
        'writers_names',
        'title',
        'description',
        'genre'
    ]

    max_docs: int = 250
    limit: int = 25

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

    async def get_many(
            self,
            query_films
        ):

        es_query = dict()
        es_query['size'] = self.max_docs

        if query_films.query:
            es_query['query'] = get_query(
                fields=self.search_fields,
                query=query_films.query
            )
        es_query['sort'] = [get_sort(query_films.sort)]
        result = await self.elastic.search(index='movies', body=es_query)

        data = []
        for doc in result['hits']['hits']:
            data.append(doc['_source'])

        if query_films.page:
            pass

        return data[:self.limit]

        # total = result.get('hits', {}).get('total', {}).get('value', {})
        # if total:
        #     data = result['hits']['hits'][0]['_source']
        #     page = query_films.page
        #
        #     if page:
        #         if page * self.limit > total:
        #             return result
        #         else:
        #             skip = query_films.page * self.limit
        #             data = data[skip::self.limit]
        #     return data



    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get('movies', film_id)
            print('ES', doc['_source'])
        except Exception as err:
            print(err)
            return None
        return Film(**doc['_source'])

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        # Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get
        data = await self.redis.get(film_id)
        print('REDIS', data)
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


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
