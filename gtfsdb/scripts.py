import click
import json
import os.path
import sys

from joblib import Parallel, delayed
from sqlalchemy.orm.exc import NoResultFound

from gtfsdb.model.db import Database
from gtfsdb.model.metaTracking import FeedFile
from gtfsdb.api import create_shapes_geom, get_gtfs_feeds, database_load_versioned, get_feeds_from_directory
from gtfsdb.config import DEFAULT_CONFIG_FILE
from gtfsdb.model.shape import ShapeGeom


@click.option('--database', help="The database connection string. This is needed if you dont have a config file located in '/etc/censio/gtfsdb.json' See sample config file in repo root")
@click.group()
@click.pass_context
def gtfsdb_main(ctx, database):
    """Simple program that greets NAME for a total of COUNT times."""
    ctx.obj = dict()
    if not database and os.path.exists(DEFAULT_CONFIG_FILE):
        conf = json.load(open(DEFAULT_CONFIG_FILE, 'r'))
        database = conf['database']
        ctx.obj.update(dict(conf=conf))
    else:
        click.echo("No database selected!!")
        sys.exit(1)
    ctx.obj.update(dict(database=Database(url=database), db_url=database))


@gtfsdb_main.command('create-geometry', help='Generate the_geom columns. This operation is indepotent, it finds the list shapes without geoms and parses those')
@click.option('-p', '--parallel', default=1, help='Number of worker processes')
@click.pass_context
def create_geom(ctx, parallel):
    session = ctx.obj['database'].get_session()
    shape_list = ShapeGeom.get_shape_list(session)
    Parallel(n_jobs=parallel)(delayed(create_shapes_geom)(db_url=ctx.obj['db_url'],
                                                          shape_id=shape_id[0]) for shape_id in shape_list)


@gtfsdb_main.command('drop-index', help='Remove the indexes (useful for loading) This does not remove GiST indexes.')
@click.pass_context
def drop_index(ctx):
    ctx.obj['database'].drop_indexes()


@gtfsdb_main.command('create-index', help='Creates the indexes (but not the geometry indexes... do those manually')
@click.pass_context
def create(ctx):
    ctx.obj['database'].create_indexes()

@gtfsdb_main.command('load-ex-feeds')
@click.option('-p', '--parallel', default=1, help='Number of worker processes')
@click.argument('feeds', nargs=-1)
@click.pass_context
def load_gtfs_ex(ctx, feeds, parallel):
    db = ctx.obj['database']
    db.create()
    feeds = set(get_gtfs_feeds(db.get_session(), feeds))
    click.echo("Ready to load {} feeds".format(len(feeds)))
    load_feeds(feeds, db, parallel)

@gtfsdb_main.command('delete-feed-file', help='delete a feed file by MD5 Sum. This is a cascading operation.')
@click.argument('file_id_list', nargs=-1)
@click.pass_context
def delete_feed_file(ctx, file_id_list):
    session = ctx.obj['database'].get_session()
    for file_id in file_id_list:
        try:
            feed_file = session.query(FeedFile).get(file_id)
        except NoResultFound:
            click.echo("Could not find file with id: {}".format(file_id))
            sys.exit(1)
        name = feed_file.filename
        click.echo("found feed file: {} ({})".format(name, file_id))
        session.delete(feed_file)
        session.commit()
        session.close()
        click.echo("sucessfully deleted feed file: {} ({})".format(name, file_id))

@gtfsdb_main.command('add-by-zip', help='Pass a GTFS zip or a directory tree containing zips, and it will import those')
@click.argument('directory', nargs=1)
@click.option('-p', '--parallel', default=1, help='Number of worker processes')
@click.pass_context
def add_feed_zip(ctx, parallel, directory):
    db = ctx.obj['database']
    db.create()
    feed_list = get_feeds_from_directory(directory)
    click.echo("Ready to load {} feeds".format(len(feed_list)))
    load_feeds(feed_list, db, parallel)

def load_feeds(feeds, database, parallel=0):
    database.drop_indexes()
    if parallel:
        concurrent_run(feeds, database.url, parallel)
    else:
        serial_run(feeds, database.url)


def serial_run(sources, database):
    for source in sources:
        database_load_versioned(db_url=database, feed_file=source)


def concurrent_run(sources, database, num_jobs):
    Parallel(n_jobs=int(num_jobs))(delayed(database_load_versioned)(db_url=database, feed_file=source) for source in sources)
