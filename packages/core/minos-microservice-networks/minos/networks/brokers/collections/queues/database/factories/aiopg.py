from abc import (
    ABC,
    abstractmethod,
)
from collections.abc import (
    Iterable,
)

from psycopg2.sql import (
    SQL,
)

from minos.common import (
    AiopgDatabaseOperation,
    DatabaseOperation,
)

from .abc import (
    BrokerQueueDatabaseOperationFactory,
)


# noinspection SqlResolve,SqlNoDataSourceInspection,SqlNoDataSourceInspection,SqlResolve
class AiopgBrokerQueueDatabaseOperationFactory(BrokerQueueDatabaseOperationFactory, ABC):
    """Aiopg Broker Queue Database Operation Factory class."""

    @abstractmethod
    def build_table_name(self) -> str:
        """Get the table name.

        :return: A ``str`` value.
        """
        raise NotImplementedError

    def build_create_table(self) -> DatabaseOperation:
        """Build the "create table" query.

        :return: A ``SQL`` instance.
        """
        return AiopgDatabaseOperation(
            SQL(
                f"CREATE TABLE IF NOT EXISTS {self.build_table_name()} ("
                "id BIGSERIAL NOT NULL PRIMARY KEY, "
                "topic VARCHAR(255) NOT NULL, "
                "data BYTEA NOT NULL, "
                "retry INTEGER NOT NULL DEFAULT 0, "
                "processing BOOL NOT NULL DEFAULT FALSE, "
                "created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), "
                "updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW())"
            ),
            lock=self.build_table_name(),
        )

    def build_update_not_processed(self, id_: int) -> DatabaseOperation:
        """Build the "update not processed" query.

        :return: A ``SQL`` instance.
        """
        return AiopgDatabaseOperation(
            SQL(
                f"UPDATE {self.build_table_name()} "
                "SET processing = FALSE, retry = retry + 1, updated_at = NOW() WHERE id = %(id)s"
            ),
            {"id": id_},
        )

    def build_delete_processed(self, id_: int) -> DatabaseOperation:
        """Build the "delete processed" query.

        :return: A ``SQL`` instance.
        """
        return AiopgDatabaseOperation(
            SQL(f"DELETE FROM {self.build_table_name()} WHERE id = %(id)s"),
            {"id": id_},
        )

    def build_mark_processing(self, ids: Iterable[int]) -> DatabaseOperation:
        """

        :return: A ``SQL`` instance.
        """
        return AiopgDatabaseOperation(
            SQL(f"UPDATE {self.build_table_name()} SET processing = TRUE WHERE id IN %(ids)s"),
            {"ids": tuple(ids)},
        )

    def build_count_not_processed(self, retry: int, *args, **kwargs) -> DatabaseOperation:
        """Build the "count not processed" query.

        :return:
        """
        return AiopgDatabaseOperation(
            SQL(
                f"SELECT COUNT(*) FROM (SELECT id FROM {self.build_table_name()} "
                "WHERE NOT processing AND retry < %(retry)s FOR UPDATE SKIP LOCKED) s"
            ),
            {"retry": retry},
        )

    def build_insert(self, topic: str, data: bytes) -> DatabaseOperation:
        """Build the "insert" query.

        :return: A ``SQL`` instance.
        """
        return AiopgDatabaseOperation(
            SQL(f"INSERT INTO {self.build_table_name()} (topic, data) VALUES (%(topic)s, %(data)s) RETURNING id"),
            {"topic": topic, "data": data},
        )

    def build_select_not_processed(self, retry: int, records: int, *args, **kwargs) -> DatabaseOperation:
        """Build the "select not processed" query.

        :return: A ``SQL`` instance.
        """
        return AiopgDatabaseOperation(
            SQL(
                "SELECT id, data "
                f"FROM {self.build_table_name()} "
                "WHERE NOT processing AND retry < %(retry)s "
                "ORDER BY created_at "
                "LIMIT %(records)s "
                "FOR UPDATE "
                "SKIP LOCKED"
            ),
            {
                "retry": retry,
                "records": records,
            },
        )
