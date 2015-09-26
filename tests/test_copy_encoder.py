__author__ = 'rhunter'

import unittest
import uuid
from datetime import datetime

from gtfsdb.model.copy_encoder import PSQLCopyWriter

class TestEncoder(unittest.TestCase):

    def test_encoder_uuid(self):
        test_uuid = 'cfb03b54-179b-4398-8ce2-1a9a0a3bb138'
        input = dict(stop_id=uuid.UUID(test_uuid), head_sign=None)
        ret_val = PSQLCopyWriter.encode_input(input)
        self.assertEqual(test_uuid.replace('-', ''), ret_val['stop_id'])

    def test_encoder_bool(self):
        input = dict(completed=True, bad=False, test=123)
        ret_val = PSQLCopyWriter.encode_input(input)
        self.assertEqual('t', ret_val['completed'])
        self.assertEqual('f', ret_val['bad'])
        self.assertEqual(123, ret_val['test'])

    def test_datetime(self):
        input = dict(time=datetime(2015, 9, 26, 16, 25, 57))
        ret_val = PSQLCopyWriter.encode_input(input)
        self.assertEqual('2015-09-26 16:25:57', ret_val['time'])
        input = dict(time=datetime(2015, 9, 26, 16, 25, 57, 23423))
        ret_val = PSQLCopyWriter.encode_input(input)
        self.assertEqual('2015-09-26 16:25:57.023423', ret_val['time'])

