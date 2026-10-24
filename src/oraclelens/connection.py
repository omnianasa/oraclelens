import oracledb

from oraclelens.config import OracleLensConfig


class OracleConnectionManager:
    def __init__(self, config: OracleLensConfig):
        self.config = config
        self._connection = None

    def connect(self):
        if self._connection is not None:
            return self._connection

        self.config.validate()

        self._connection = oracledb.connect(
            user=self.config.user,
            password=self.config.password,
            dsn=self.config.dsn,
        )

        return self._connection

    def close(self) -> None:
        if self._connection is not None:
            try:
                self._connection.close()
            finally:
                self._connection = None

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()