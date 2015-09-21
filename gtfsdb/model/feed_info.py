from sqlalchemy import Column, Sequence
from sqlalchemy.types import Date, DateTime, String, Integer, Boolean
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session

from gtfsdb import config
from gtfsdb.model.base import Base
import logging

log = logging.getLogger(__name__)




class FeedInfo(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'feed_info.txt'

    __tablename__ = 'gtfs_feed_info'
    #TODO create relation with agency to handle cases where multiple agency for single provider

    agency_id = Column(String(255), primary_key=True)
    feed_publisher_name = Column(String(255))
    feed_publisher_url = Column(String(255), nullable=False)
    feed_lang = Column(String(255), nullable=False)
    feed_start_date = Column(Date)
    feed_end_date = Column(Date)
    feed_version = Column(String(255))
    feed_license = Column(String(255))

    @classmethod
    def load(cls, db, **kwargs):
        try:
            super(FeedInfo, cls).load(db, **kwargs)
        except IntegrityError, e:
            log.warning(e)


#class DataexchangeInfo(AgencyBase):
#
#    __tablename__ = "gtfs_meta"
#
#    dataexchange_id = Column(String(255), primary_key=True, nullable=False)
#    file_name = Column(String(255))
#    file_url = Column(String(255))
#    file_checksum = Column(String(32))
#    date_added = Column(Integer)
#    completed = Column(Boolean, default=False)
#    completed_on = Column(DateTime)
#
#    @classmethod
#    def overwrite(cls, db, new_record):
#        session = db.get_session()
#        old_record = session.query(DataexchangeInfo).get(new_record.dataexchange_id)
#        if not old_record or not old_record.completed \
#            or old_record.date_added < new_record.date_added:
#            session.merge(new_record)
#            session.commit()
#            return True
#        return False

