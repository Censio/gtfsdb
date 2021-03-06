import datetime
import time
import sys
import logging
log = logging.getLogger(__name__)

from sqlalchemy import Column, ForeignKey, Sequence, Index
from sqlalchemy.orm import deferred, relationship
from sqlalchemy.types import Integer, String
from sqlalchemy.sql import func
from geoalchemy2 import Geometry

from gtfsdb import config
from gtfsdb.model.base import Base
from gtfsdb.model.agency import Agency
from gtfsdb.model.guuid import GUID

__all__ = ['RouteType', 'Route', 'RouteDirection', 'RouteStop', 'RouteFilter']


class RouteType(Base):
    datasource = config.DATASOURCE_LOOKUP
    filename = 'route_type.txt'
    __tablename__ = 'gtfs_route_type'

    route_type = Column(Integer, primary_key=True, autoincrement=False)
    route_type_name = Column(String(255))
    route_type_desc = Column(String(255))


class Route(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'routes.txt'

    __tablename__ = 'gtfs_routes'

    route_id = Column(GUID(), primary_key=True, nullable=False)
    agency_id = Column(GUID(), nullable=False)
    route_short_name = Column(String(255))
    route_long_name = Column(String(255))
    route_desc = Column(String(255))
    route_type = Column(Integer, nullable=False)
    route_url = Column(String(255))
    route_color = Column(String(6))
    route_text_color = Column(String(6))
    route_sort_order = Column(Integer)

    trips = relationship('Trip', primaryjoin='Trip.route_id==Route.route_id',
                         foreign_keys='(Trip.route_id)', uselist=True, backref='route',
                         cascade='delete')

    directions = relationship('RouteDirection', primaryjoin='RouteDirection.route_id==Route.route_id',
                              foreign_keys='(RouteDirection.route_id)', uselist=True, cascade='delete',
                              backref='route')

    fare_rules = relationship('FareRule', primaryjoin='FareRule.route_id==Route.route_id',
                              foreign_keys='(FareRule.route_id)', cascade='delete', backref='route')

    @classmethod
    def make_record(cls, row, key_lookup, **kwargs):
        if 'agency_id' not in row.keys() or not row['agency_id']:
            row['agency_id']='1'
        return super(Route, cls).make_record(row, key_lookup)

    @property
    def is_active(self, date=None):
        """ :return False whenever we see that the route start and end date are outside the
                    input date (where the input date defaults to 'today')
        """
        ret_val = True
        if self.start_date and self.end_date:
            if date is None:
                date = datetime.date.today()
            ret_val = False
            if self.start_date <= date <= self.end_date:
                ret_val = True
        return ret_val

    @property
    def route_name(self, fmt="{self.route_short_name}-{self.route_long_name}"):
        ''' build a route name out of long and short names...
        '''
        if not self.is_cached_data_valid('_route_name'):
            log.warn("query route name")
            ret_val = self.route_long_name
            if self.route_long_name and self.route_short_name:
                ret_val = fmt.format(self=self)
            elif self.route_long_name is None:
                ret_val = self.route_short_name
            self._route_name = ret_val
            self.update_cached_data('_route_name')

        return self._route_name

    def direction_name(self, direction_id, def_val=''):
        ret_val = def_val
        try:
            dir = self.directions.filter(RouteDirection.direction_id==direction_id)
            if dir and dir.direction_name:
                ret_val = dir.direction_name
        except:
            pass
        return ret_val

    @property
    def _get_start_end_dates(self):
        '''find the min & max date using Trip & UniversalCalendar'''
        if not self.is_cached_data_valid('_start_date'):
            from gtfsdb.model.calendar import UniversalCalendar
            q = self.session.query(func.min(UniversalCalendar.date), func.max(UniversalCalendar.date))
            q = q.filter(UniversalCalendar.trips.any(route_id=self.route_id))
            self._start_date, self._end_date = q.one()
            self.update_cached_data('_start_date')

        return self._start_date, self._end_date

    @property
    def start_date(self):
        return self._get_start_end_dates[0]

    @property
    def end_date(self):
        return self._get_start_end_dates[1]

    @classmethod
    def active_routes(cls, session, date=None):
        ''' returns list of routes that are seen as 'active' based on dates and filters
        '''
        ret_val = []

        # step 1: grab all stops
        routes = session.query(Route).filter(~Route.route_id.in_(session.query(RouteFilter.route_id))).order_by(Route.route_sort_order).all()

        # step 2: default date
        if date is None or not isinstance(date, datetime.date):
            date = datetime.date.today()

        # step 3: filter by date
        if date:
            for r in routes:
                if r:
                    # step 3a: filter based on date (if invalid looking date objects, just pass the route on)
                    if r.start_date and r.end_date:
                        if r.start_date <= date <= r.end_date:
                            ret_val.append(r)
                    else:
                        ret_val.append(r)
        else:
            # step 3b: if no good date, just assign routes to ret_val
            ret_val = routes

        return ret_val

Index('ix_gtfs_routes_route_id', Route.route_id, postgresql_using='hash')
Index('ix_gtfs_routes_agency_id', Route.agency_id, postgresql_using='hash')


class RouteDirection(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'route_directions.txt'

    __tablename__ = 'gtfs_directions'

    id = Column(GUID(), primary_key=True, nullable=True)
    direction_id = Column(GUID(), nullable=False)
    route_id = Column(GUID(), nullable=False)
    direction_name = Column(String(255))

Index('ix_gtfs_route_directions_direction_id', RouteDirection.direction_id, postgresql_using='hash')
Index('ix_gtfs_route_directions_route_id', RouteDirection.route_id, postgresql_using='hash')

class RouteStop(Base):
    datasource = config.DATASOURCE_DERIVED

    __tablename__ = 'route_stops'

    id = Column(GUID(), primary_key=True, nullable=True)
    route_id = Column(GUID(), nullable=False)
    direction_id = Column(GUID(), nullable=False)
    stop_id = Column(GUID(), nullable=False)
    order = Column(Integer, nullable=False)

    route = relationship(
        'Route',
        primaryjoin='RouteStop.route_id==Route.route_id',
        foreign_keys='(RouteStop.route_id)',
        uselist=False, viewonly=True, lazy='joined')

    stop = relationship(
        'Stop',
        primaryjoin='RouteStop.stop_id==Stop.stop_id',
        foreign_keys='(RouteStop.stop_id)',
        uselist=False, viewonly=True, lazy='joined')

    direction = relationship(
        'RouteDirection',
        primaryjoin='RouteStop.route_id==RouteDirection.route_id and RouteStop.direction_id==RouteDirection.direction_id',
        foreign_keys='(RouteStop.route_id, RouteStop.direction_id)',
        uselist=False, viewonly=True, lazy='joined')

    @classmethod
    def load(cls, db, **kwargs):
        ''' for each route/direction, find list of stop_ids for route/direction pairs

            the load is a two part process, where part A finds a list of unique stop ids, and
            part B creates the RouteStop (and potentially RouteDirections ... if not in GTFS) records
        '''
        #TODO: This is inactive until we associate agency ID with all records
        start_time = time.time()
        session = db.session
        routes = session.query(Route).all()

        # step 0: for each route...
        for r in routes:

            # step 1: filter the list of trips down to only a trip with a unique pattern
            #   TODO: any way to have the orm do this?  Something probably really simple Mike?
            trips = []
            shape_id_filter = []
            for t in r.trips:
                if t.shape_id not in shape_id_filter:
                    shape_id_filter.append(t.shape_id)
                    trips.append(t)

            # step 2: sort our list of trips by length (note: for trips with two directions, ...)
            trips = sorted(trips, key=lambda t: t.trip_len, reverse=True)

            # PART A: we're going to just collect a list of unique stop ids for this route / directions 
            for d in [0, 1]:
                unique_stops_ids = []

                # step 3: loop through all our trips and their stop times, pulling out a unique set of stops 
                for t in trips:
                    if t.direction_id == d:

                        # step 4: loop through this trip's stop times, and find any/all stops that are in our stop list already
                        #         further, let's try to find the best position of that stop (e.g., look for where the stop patterns breaks)
                        last_pos = None 
                        for i, st in enumerate(t.stop_times):
                            # step 5a: make sure this stop that customers can actually board...
                            if st.is_boarding_stop():
                                if st.stop_id in unique_stops_ids:
                                    last_pos = unique_stops_ids.index(st.stop_id)
                                else:
                                    # step 5b: add ths stop id to our unique list ... either in position, or appended to the end of the list
                                    if last_pos:
                                        last_pos += 1
                                        unique_stops_ids.insert(last_pos, st.stop_id)
                                    else:
                                        unique_stops_ids.append(st.stop_id)

                # PART B: add records to the database ...
                if len(unique_stops_ids) > 0:

                    # step 6: if a RouteDirection doesn't exist, let's create it...
                    if r.directions is None or len(r.directions) == 0:
                        rd = RouteDirection()
                        rd.route_id = r.route_id
                        rd.direction_id = d
                        rd.direction_name = "Outbound" if d is 0 else "Inbound"
                        session.add(rd)

                    # step 7: create new RouteStop records
                    for k, stop_id in enumerate(unique_stops_ids):
                        # step 4b: create a RouteStop record
                        rs = RouteStop()
                        rs.route_id = r.route_id
                        rs.direction_id = d
                        rs.stop_id = stop_id
                        rs.order = k + 1
                        session.add(rs)

                    # step 8: flush the new records to the db...
                    sys.stdout.write('*')
                    session.commit()
                    session.flush()
                    unique_stops_ids = [None]

        session.commit()
        session.close()

        processing_time = time.time() - start_time
        log.debug('{0}.load ({1:.0f} seconds)'.format(cls.__name__, processing_time))

Index('ix_gtfs_route_stops_route_id', RouteStop.route_id, postgresql_using='hash')
Index('ix_gtfs_route_stops_direction_id', RouteStop.direction_id, postgresql_using='hash')
Index('ix_gtfs_route_stops_stop_id', RouteStop.stop_id, postgresql_using='hash')


class RouteFilter(Base):
    ''' list of filters to be used to cull routes from certain lists
        e.g., there might be Shuttles that you never want to be shown...you can load that data here, and
        use it in your queries
    '''
    datasource = config.DATASOURCE_LOOKUP
    filename = 'route_filter.txt'
    __tablename__ = 'route_filters'

    route_id = Column(GUID(), primary_key=True, nullable=False)
    description = Column(String)


Index('ix_gtfs_route_filter_route_id', RouteFilter.route_id, postgresql_using='hash')
