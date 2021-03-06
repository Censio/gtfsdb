import logging
log = logging.getLogger(__file__)

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import DBAPIError, IntegrityError, ProgrammingError
import concurrent.futures
from gtfsdb import config
from math import pow
import time


class Database(object):

    def __init__(self, **kwargs):
        '''
        keyword arguments:
            is_geospatial: if database supports geo functions
            schema: database schema name
            tables: limited list of tables to load into database
            url: SQLAlchemy database url
        '''
        self.tables = kwargs.get('tables', None)
        self.url = kwargs.get('url', config.DEFAULT_DATABASE_URL)
        self.schema = kwargs.get('schema', config.DEFAULT_SCHEMA)
        self.is_geospatial = kwargs.get('is_geospatial', config.DEFAULT_IS_GEOSPATIAL)

    @property
    def classes(self):
        from gtfsdb.model.base import Base
        if self.tables:
            return [c for c in Base.__subclasses__() if c.__tablename__ in self.tables]
        return Base.__subclasses__()

    def create(self):
        '''Drop/create GTFS database'''
        from gtfsdb.model.base import Base
        Base.metadata.create_all(self.engine)

    def drop_all(self):
        from gtfsdb.model.base import Base
        Base.metadata.drop_all(self.engine)

    @property
    def dialect_name(self):
        return self.engine.url.get_dialect().name

    @property
    def metadata(self):
        from gtfsdb.model.base import Base
        return Base.metadata

    @property
    def is_geospatial(self):
        return self._is_geospatial

    @is_geospatial.setter
    def is_geospatial(self, val):
        self._is_geospatial = val
        for cls in self.classes:
            if val and hasattr(cls, 'add_geometry_column'):
                cls.add_geometry_column()

    @property
    def is_postgresql(self):
        return 'postgres' in self.dialect_name

    @property
    def is_sqlite(self):
        return 'sqlite' in self.dialect_name

    @property
    def schema(self):
        return self._schema

    @schema.setter
    def schema(self, val):
        self._schema = val
        for cls in self.classes:
            cls.__table__.schema = val

    def sorted_classes(self, key=None):
        if key:
            sorted_classes = []
            for cls in self._sort_classes(config.SORTED_CLASS_NAMES):
                if key(cls):
                   sorted_classes.append(cls)
            return sorted_classes
        return self._sort_classes(config.SORTED_CLASS_NAMES)

    @property
    def bootstrap_classes(self):
        return self._sort_classes(config.INITIAL_LOAD_CLASS)

    def _sort_classes(self, names):
        classes = []
        for class_name in names:
            cls = next((c for c in self.classes if c.__name__ == class_name), None)
            if cls:
                classes.append(cls)
        return classes

    def drop_indexes(self):
        for table_name, table in self.metadata.tables.iteritems():
            for index in table.indexes:
                try:
                    index.drop(bind=self.engine)
                except ProgrammingError:
                    continue

    def create_indexes(self):
        thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=config.DB_THREADS)
        futures = []
        for table_name, table in self.metadata.tables.iteritems():
            for index in table.indexes:
                futures.append(thread_pool.submit(index.create, bind=self.engine))
        for future in futures:
            while future.running():
                time.sleep(0.1)

    @property
    def url(self):
        return self._url

    def execute(self, command, values):
        return self.engine.execute(command, values)
        #tries = 0
        #while tries < config.DB_ATTEMPTS:
        #    try:
        #        return self.engine.execute(command, values)
        #    except IntegrityError, e:
        #        raise e
        #    except DBAPIError, e:
        #        tries += 1
        #        log.warning("Got a db error: {} Attempt: #{}".format(e, tries))
        #        time.sleep(pow(2, tries)) #exponential backoff time
        #        continue
        #log.error("Too manny attempts, failing hard!")

    def get_session(self):
        return self.session_factory()

    @url.setter
    def url(self, val):
        self._url = val
        self.engine = create_engine(val)
        if self.is_sqlite:
            self.engine.connect().connection.connection.text_factory = str
        self.session_factory = sessionmaker(self.engine)
        self.session=scoped_session(self.session_factory)
