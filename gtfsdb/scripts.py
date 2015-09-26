import click
import json
import os.path
import sys

from joblib import Parallel, delayed

from gtfsdb.model.db import Database
from gtfsdb.api import create_shapes_geoms, get_gtfs_feeds, database_load_versioned
from gtfsdb.config import DEFAULT_CONFIG_FILE


@click.option('--database', help="The database connection string")
@click.group()
@click.pass_context
def gtfsdb(ctx, database):
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

@gtfsdb.command('create-geometry')
@click.pass_context
def create_geom(ctx):
    create_shapes_geoms(ctx.obj['db_url'])


@gtfsdb.command('drop-index')
@click.pass_context
def drop_index(ctx):
    ctx.obj['database'].drop_indexes()


@gtfsdb.command('create-index')
@click.pass_context
def create(ctx):
    ctx.obj['database'].create_indexes()

@gtfsdb.command('load-ex-feeds')
@click.option('-p', '--parallel', default=1, help='Number of worker processes')
@click.pass_context
def load_gtfs_ex(ctx, parallel):
    db = ctx.obj['database']
    feeds = set(get_gtfs_feeds(db.get_session()))
    click.echo("Ready to load {} feeds".format(len(feeds)))
    load_feeds(feeds, db, parallel)


def load_feeds(feeds, database, parallel=0):
    database.create()
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
