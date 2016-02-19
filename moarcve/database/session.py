from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from moarcve.database.base import Base
from contextlib import contextmanager

def get_connector(conf, db_type):

    if db_type == 'sqlite':
        return 'sqlite:///%s' % conf.get('database.sqlite', 'path')
    elif db_type == 'mysql':
        def cg(key):
            """Helper"""
            return conf.get('db.mysql', key)
        return "mysql+mysqlconnector://" \
            "{username}:{password}@{host}:{port}/{name}".format(
                username=cg('username'),
                password=cg('password'),
                host=cg('host'),
                port=cg('port'),
                name=cg('name'))

def get_engine(conf):
    db_type = conf.get('database', 'use')
    connector = get_connector(conf, db_type)
    engine = None
    if db_type == 'mysql':
        engine = create_engine(connector,
                       convert_unicode=True, 
                       pool_size=2,
                       max_overflow=100)
    elif db_type == 'sqlite':
        engine = create_engine(connector)
    else:
        raise RuntimeError('Invalid db type: %s' % db_type)
    return connector, engine

Session = None

@contextmanager
def session_scope():
    global Session
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
        session.rollback()
    except:
        raise
    finally:
        session.close()

def init(conf):
    global Session
    if Session is None:
        print('Init engine')
        _connector, engine = get_engine(conf)
        Session = sessionmaker()
        Session.configure(bind=engine)
        if conf.getboolean('database', 'drop_table_on_start'):
            Base.metadata.drop_all(engine)  # @UndefinedVariable
        Base.metadata.create_all(engine)  # @UndefinedVariable
