from pg_to_es import movies
from settings import es_dsl
from db.es_db import ElasticBase
from loguru import logger
from pg_to_es.schema import schema
import time



def create_index(es_db, index, settings, mappings):
    res = es_db.client.indices.create(
      index=index,
      settings=settings,
      mappings=mappings,
      ignore=400
    )
    logger.info(f'{index}, {res}')


if __name__ == '__main__':
    print(es_dsl)
    with ElasticBase(es_dsl) as es_db:
        create_index(
            es_db,
            'movies',
            settings=schema.settings,
            mappings=schema.mappings
        )

    while True:
        movies.run()
        time.sleep(5)


