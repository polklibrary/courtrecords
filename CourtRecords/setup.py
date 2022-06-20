import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'chameleon==2.11',
	'pyramid==1.3.3',
    'pymysql==0.5',
	'mako==0.7.3',
    'SQLAlchemy==0.7.8',
    'transaction',
    'pyramid_tm==0.7',
    'pyramid_mailer==0.11',
    'repoze.sendmail==4.0',
    'MarkupSafe==0.23',
    'zope.sqlalchemy==0.7.5',
    'waitress==0.8.9',
    'requests==2.5.3',
    'transaction==1.4.3',
    'zope.deprecation==4.1.2',
    'zope.interface==4.1.2',
    ]

setup(name='CourtRecords',
      version='0.0',
      description='CourtRecords',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='courtrecords',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = courtrecords:main
      [console_scripts]
      initialize_ArchivesIndexes_db = courtrecords.scripts.initializedb:main
      """,
      )

