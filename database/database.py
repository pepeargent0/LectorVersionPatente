from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sshtunnel import SSHTunnelForwarder
from config.config import get_config_ssh

engine = None
Session = None


def init_database(db_url):
    """
    global engine, Session
    engine = create_engine(db_url, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    engine.connect()
    """
    global engine, Session
    config_ssh = get_config_ssh()
    with SSHTunnelForwarder(
            (config_ssh.host, config_ssh.port),
            ssh_username=config_ssh.username,
            ssh_password=config_ssh.password,
            remote_bind_address=('localhost', 3306)
    ) as tunnel:
        db_host = tunnel.local_bind_host
        db_port = tunnel.local_bind_port

        # db_url_with_tunnel = f'mysql+pymysql://<DB_USERNAME>:<DB_PASSWORD>@{db_host}:{db_port}/<DB_NAME>'
        engine = create_engine(db_url, pool_pre_ping=True)
        # engine = create_engine(db_url_with_tunnel, pool_pre_ping=True)
        Session = sessionmaker(bind=engine)
        engine.connect()


def init_sin_tunel_database(db_url):
    """
    global engine, Session
    engine = create_engine(db_url, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    engine.connect()
    """
    global engine, Session
    engine = create_engine(db_url, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    engine.connect()


def get_session():
    return Session()
