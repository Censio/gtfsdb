"""set_index

Revision ID: 29839c533f78
Revises: 
Create Date: 2015-09-24 12:18:12.775006

"""

# revision identifiers, used by Alembic.
revision = '29839c533f78'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_gtfs_agency_agency_id'), 'gtfs_agency', ['agency_id'], unique=False)
    op.create_index(op.f('ix_gtfs_agency_feed_id'), 'gtfs_agency', ['feed_id'], unique=False)
    op.create_index(op.f('ix_gtfs_calendar_service_id'), 'gtfs_calendar', ['service_id'], unique=False)
    op.create_index(op.f('ix_gtfs_calendar_dates_service_id'), 'gtfs_calendar_dates', ['service_id'], unique=False)
    op.create_index(op.f('ix_gtfs_directions_direction_id'), 'gtfs_directions', ['direction_id'], unique=False)
    op.create_index(op.f('ix_gtfs_directions_route_id'), 'gtfs_directions', ['route_id'], unique=False)
    op.create_index(op.f('ix_gtfs_fare_attributes_fare_id'), 'gtfs_fare_attributes', ['fare_id'], unique=False)
    op.create_index(op.f('ix_gtfs_fare_rules_fare_id'), 'gtfs_fare_rules', ['fare_id'], unique=False)
    op.create_index(op.f('ix_gtfs_feed_info_feed_id'), 'gtfs_feed_info', ['feed_id'], unique=False)
    op.create_index(op.f('ix_gtfs_frequencies_trip_id'), 'gtfs_frequencies', ['trip_id'], unique=False)
    op.create_index(op.f('ix_gtfs_route_type_route_type'), 'gtfs_route_type', ['route_type'], unique=False)
    op.create_index(op.f('ix_gtfs_routes_agency_id'), 'gtfs_routes', ['agency_id'], unique=False)
    op.create_index(op.f('ix_gtfs_routes_route_id'), 'gtfs_routes', ['route_id'], unique=False)
    op.create_index(op.f('ix_gtfs_shape_geoms_shape_id'), 'gtfs_shape_geoms', ['shape_id'], unique=False)
    op.create_index(op.f('ix_gtfs_shapes_shape_id'), 'gtfs_shapes', ['shape_id'], unique=False)
    op.create_index(op.f('ix_gtfs_stop_times_stop_id'), 'gtfs_stop_times', ['stop_id'], unique=False)
    op.create_index(op.f('ix_gtfs_stop_times_trip_id'), 'gtfs_stop_times', ['trip_id'], unique=False)
    op.create_index(op.f('ix_gtfs_stops_stop_id'), 'gtfs_stops', ['stop_id'], unique=False)
    op.create_index(op.f('ix_gtfs_transfers_from_stop_id'), 'gtfs_transfers', ['from_stop_id'], unique=False)
    op.create_index(op.f('ix_gtfs_transfers_to_stop_id'), 'gtfs_transfers', ['to_stop_id'], unique=False)
    op.create_index(op.f('ix_gtfs_trips_direction_id'), 'gtfs_trips', ['direction_id'], unique=False)
    op.create_index(op.f('ix_gtfs_trips_route_id'), 'gtfs_trips', ['route_id'], unique=False)
    op.create_index(op.f('ix_gtfs_trips_service_id'), 'gtfs_trips', ['service_id'], unique=False)
    op.create_index(op.f('ix_gtfs_trips_shape_id'), 'gtfs_trips', ['shape_id'], unique=False)
    op.create_index(op.f('ix_gtfs_trips_trip_id'), 'gtfs_trips', ['trip_id'], unique=False)
    op.create_index(op.f('ix_route_filters_route_id'), 'route_filters', ['route_id'], unique=False)
    op.create_index(op.f('ix_route_stops_direction_id'), 'route_stops', ['direction_id'], unique=False)
    op.create_index(op.f('ix_route_stops_order'), 'route_stops', ['order'], unique=False)
    op.create_index(op.f('ix_route_stops_route_id'), 'route_stops', ['route_id'], unique=False)
    op.create_index(op.f('ix_route_stops_stop_id'), 'route_stops', ['stop_id'], unique=False)
    op.create_index(op.f('ix_stop_features_stop_id'), 'stop_features', ['stop_id'], unique=False)
    op.create_index(op.f('ix_universal_calendar_service_id'), 'universal_calendar', ['service_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_universal_calendar_service_id'), table_name='universal_calendar')
    op.drop_index(op.f('ix_stop_features_stop_id'), table_name='stop_features')
    op.drop_index(op.f('ix_route_stops_stop_id'), table_name='route_stops')
    op.drop_index(op.f('ix_route_stops_route_id'), table_name='route_stops')
    op.drop_index(op.f('ix_route_stops_order'), table_name='route_stops')
    op.drop_index(op.f('ix_route_stops_direction_id'), table_name='route_stops')
    op.drop_index(op.f('ix_route_filters_route_id'), table_name='route_filters')
    op.drop_index(op.f('ix_gtfs_trips_trip_id'), table_name='gtfs_trips')
    op.drop_index(op.f('ix_gtfs_trips_shape_id'), table_name='gtfs_trips')
    op.drop_index(op.f('ix_gtfs_trips_service_id'), table_name='gtfs_trips')
    op.drop_index(op.f('ix_gtfs_trips_route_id'), table_name='gtfs_trips')
    op.drop_index(op.f('ix_gtfs_trips_direction_id'), table_name='gtfs_trips')
    op.drop_index(op.f('ix_gtfs_transfers_to_stop_id'), table_name='gtfs_transfers')
    op.drop_index(op.f('ix_gtfs_transfers_from_stop_id'), table_name='gtfs_transfers')
    op.drop_index(op.f('ix_gtfs_stops_stop_id'), table_name='gtfs_stops')
    op.drop_index(op.f('ix_gtfs_stop_times_trip_id'), table_name='gtfs_stop_times')
    op.drop_index(op.f('ix_gtfs_stop_times_stop_id'), table_name='gtfs_stop_times')
    op.drop_index(op.f('ix_gtfs_shapes_shape_id'), table_name='gtfs_shapes')
    op.drop_index(op.f('ix_gtfs_shape_geoms_shape_id'), table_name='gtfs_shape_geoms')
    op.drop_index(op.f('ix_gtfs_routes_route_id'), table_name='gtfs_routes')
    op.drop_index(op.f('ix_gtfs_routes_agency_id'), table_name='gtfs_routes')
    op.drop_index(op.f('ix_gtfs_route_type_route_type'), table_name='gtfs_route_type')
    op.drop_index(op.f('ix_gtfs_frequencies_trip_id'), table_name='gtfs_frequencies')
    op.drop_index(op.f('ix_gtfs_feed_info_feed_id'), table_name='gtfs_feed_info')
    op.drop_index(op.f('ix_gtfs_fare_rules_fare_id'), table_name='gtfs_fare_rules')
    op.drop_index(op.f('ix_gtfs_fare_attributes_fare_id'), table_name='gtfs_fare_attributes')
    op.drop_index(op.f('ix_gtfs_directions_route_id'), table_name='gtfs_directions')
    op.drop_index(op.f('ix_gtfs_directions_direction_id'), table_name='gtfs_directions')
    op.drop_index(op.f('ix_gtfs_calendar_dates_service_id'), table_name='gtfs_calendar_dates')
    op.drop_index(op.f('ix_gtfs_calendar_service_id'), table_name='gtfs_calendar')
    op.drop_index(op.f('ix_gtfs_agency_feed_id'), table_name='gtfs_agency')
    op.drop_index(op.f('ix_gtfs_agency_agency_id'), table_name='gtfs_agency')
    ### end Alembic commands ###