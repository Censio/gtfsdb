from sqlalchemy import Column, Integer, Sequence, String, Index
from sqlalchemy.orm import relationship
import libuuid

from gtfsdb import config
from gtfsdb.model.base import Base
from gtfsdb.model.guuid import GUID

class Transfer(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'transfers.txt'

    __tablename__ = 'gtfs_transfers'

    id = Column(GUID(), primary_key=True, nullable=True)
    from_stop_id = Column(GUID(), nullable=False)
    to_stop_id = Column(GUID(), nullable=False)
    transfer_type = Column(Integer, default=0)
    min_transfer_time = Column(Integer)

    from_stop = relationship('Stop', primaryjoin='Stop.stop_id==Transfer.from_stop_id',
                             foreign_keys='(Transfer.from_stop_id)')
    to_stop = relationship('Stop', primaryjoin='Stop.stop_id==Transfer.to_stop_id',
                           foreign_keys='(Transfer.to_stop_id)')

    @classmethod
    def make_record(cls, row, key_lookup, **kwargs):
        row['from_stop_id'] = key_lookup['stop_id'][row['from_stop_id']]
        row['to_stop_id'] = key_lookup['stop_id'][row['to_stop_id']]
        return super(Transfer, cls).make_record(row, key_lookup)

Index('ix_gtfs_transfers_from_stop_id', Transfer.from_stop_id, postgresql_using='hash')
Index('ix_gtfs_transfers_to_stop_id', Transfer.to_stop_id, postgresql_using='hash')
