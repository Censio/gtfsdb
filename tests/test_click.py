__author__ = 'rhunter'
import unittest
import os
import hashlib
import mock

import testing.postgresql

from gtfsdb.api import database_load_versioned
from gtfsdb.model.db import Database
from gtfsdb.model.metaTracking import FeedFile
from gtfsdb.scripts import create_shapes_geom, drop_index, load_feeds, create_geom


class TestClick(unittest.TestCase):
    def setUp(self):
        self.postgresql = testing.postgresql.Postgresql()
        self.database = Database(url=self.postgresql.url())
        self.database.engine.execute('create extension postgis;')
        self.database.engine.execute('create extension postgis_topology;')
        self.database.create()
        self.root_dir = os.path.dirname(__file__)
        self.ctx = mock.Mock()
        self.ctx.obj = dict(database=self.database, db_url=self.postgresql.url())
        file_location = os.path.join(self.root_dir, 'data/sample-feed.zip')
        md5 = hashlib.md5(open(file_location, 'rb').read()).hexdigest()
        feed_file=FeedFile(md5sum=md5, file_url=file_location)
        database_load_versioned(feed_file, self.postgresql.url())

    def tearDown(self):
        self.database.session_factory.close_all()
        self.postgresql.stop()


    def test_create_geoms(self):
        create_geom(self.ctx, p=1)




