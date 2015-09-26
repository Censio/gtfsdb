__author__ = 'rhunter'

import uuid
import datetime
from StringIO import StringIO
import csv


class PSQLCopyWriter(object):
    def __init__(self, table_cls, outfile=None):
        if outfile:
            self.outfile = open(outfile, 'w')
        else:
            self.outfile = StringIO()
        self.writer = csv.DictWriter(self.out_file, fieldnames=['a','b'], delimiter='\t')

    def __del__(self):
        self.outfile.close()

    def __len__(self):
        return len(self.outfile)

    def row(self, row):
        pass


    @classmethod
    def encode_input(cls, input_dict):
        cpy_input = dict(input_dict) #lets not modify inpu
        for column, value in cpy_input.iteritems():
            if isinstance(value, uuid.UUID):
                cpy_input[column] = str(value).replace('-', '')
            elif isinstance(value, bool):
                cpy_input[column] = 't' if value else 'f'
            elif isinstance(value, datetime.datetime):
                cpy_input[column] = value.strftime('%Y-%m-%d %H:%M:%S') if value.microsecond == 0 else value.strftime('%Y-%m-%d %H:%M:%S.%f')
        return cpy_input





