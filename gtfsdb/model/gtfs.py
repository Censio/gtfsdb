from contextlib import closing
import logging
import shutil
import tempfile
import time
from urllib import urlretrieve
import zipfile
import guuid

from gtfsdb import config
from .route import Route


log = logging.getLogger(__name__)


class GTFS(object):

    def __init__(self, filename, unique_id=None):
        self.file = filename
        log.debug("Fetching {}".format(filename))
        self.local_file = urlretrieve(filename)[0]
        log.debug("Done Fetching {}".format(filename))

    @staticmethod
    def bootstrab_db(db):
        for cls in db.bootstrap_classes:
            cls.load(db)

    def load(self, db, **kwargs):
        '''Load GTFS into database'''
        start_time = time.time()
        log.debug('GTFS.load: {0}'.format(self.file))

        key_lookup = dict()

        '''load known GTFS files, derived tables & lookup tables'''
        gtfs_directory = self.unzip()
        load_kwargs = dict(
            batch_size=kwargs.get('batch_size', config.DEFAULT_BATCH_SIZE),
            gtfs_directory=gtfs_directory,
            key_lookup=key_lookup
        )
        for cls in db.sorted_classes(lambda k: k.datasource == config.DATASOURCE_GTFS):
            cls.load(db, **load_kwargs)
        shutil.rmtree(gtfs_directory)


        '''load route geometries derived from shapes.txt'''
        # Lets not use updates while importing
        #if Route in db.classes:
        #    Route.load_geoms(db)

        #for cls in db.sorted_classes(lambda k: k.datasource == config.DATASOURCE_GTFS):
        #    cls.post_process(db)

        process_time = time.time() - start_time
        log.debug('GTFS.load ({0:.0f} seconds)'.format(process_time))

    def unzip(self, path=None):
        '''Unzip GTFS files from URL/directory to path.'''
        path = path if path else tempfile.mkdtemp()
        try:
            with closing(zipfile.ZipFile(self.local_file)) as z:
                z.extractall(path)
        except Exception, e:
            log.warning(e)
        return path
