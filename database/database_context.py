import logging
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL

from time import sleep

class Singleton(type):
    _instances = {}
    def __call__(cls, *args: Any, **kwds: Any) -> Any:
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwds)
        return cls._instances[cls]


class Database:
    def __init__(self, username, password, host, port, database, driver) -> None:
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.driver = driver
        self.engine = self._get_engine()
        self.session = self._get_session()

    # Get connection to database
    def _get_engine(self):
        connection_url = URL.create(
            "mssql+pyodbc",
            username= self.username,
            password= self.password,
            host=self.host,
            port=self.port,
            database=self.database,
            query={
                "driver": self.driver
            },
        )

        # Load database engine
        return create_engine(connection_url)
        
    # Connect to database until is online for a time of two minutes
    def _wait_for_database_to_be_online(self):
        max_retries = 12
        retry_interval = 10  # seconds

        for _ in range(max_retries):
            try:
                self.engine.connect()  # Attempt to connect
                logging.info("Database is online and connection successful.")
                return True
            except Exception:
                logging.warn(f"Database is not yet online. Retrying in {retry_interval} seconds...")
                sleep(retry_interval)
        else:
            logging.error("Max retries reached. Database is still not online.")

        return False        


    def _get_session(self):
        if not self._wait_for_database_to_be_online():
            raise Exception("Could not establish a connection with the database.")
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session