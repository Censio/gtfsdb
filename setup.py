from setuptools import setup, find_packages
import sys


oracle_extras = ['cx_oracle>=5.1']
postgresql_extras = ['psycopg2>=2.4.2']
dev_extras = oracle_extras + postgresql_extras


extras_require = dict(
    dev=dev_extras,
    oracle=oracle_extras,
    postgresql=postgresql_extras,
)

install_requires = ['geoalchemy2>=0.2.4', 'sqlalchemy>=0.9', 'joblib', 'requests', 'futures', 'psycopg2', 'alembic',
                    'click', 'testing.postgresql', 'python-libuuid', 'mock']
if sys.version_info[:2] <= (2, 6):
    install_requires.append('argparse>=1.2.1')
    extras_require['dev'].append('unittest2')

setup(
    name='censio-gtfsdb',
    version='0.1.UNKNOWN',
    description='GTFS Database',
    long_description=open('README').read(),
    keywords='GTFS',
    author='Mike Gilligan',
    author_email='gilligam@trimet.org',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points='''
        [console_scripts]
        gtfsdb=gtfsdb.scripts:gtfsdb_main
    ''',
    classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
)
