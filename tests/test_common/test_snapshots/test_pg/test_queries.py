import unittest
from unittest.mock import (
    patch,
)

import aiopg
from psycopg2.extras import (
    Json,
)

from minos.common import (
    Condition,
    Ordering,
    PostgreSqlSnapshotQueryBuilder,
)
from minos.common.testing import (
    PostgresAsyncTestCase,
)
from tests.utils import (
    BASE_PATH,
)


class TestPostgreSqlSnapshotQueryBuilder(PostgresAsyncTestCase):
    CONFIG_FILE_PATH = BASE_PATH / "test_config.yml"

    def test_constructor(self):
        qb = PostgreSqlSnapshotQueryBuilder("path.to.Aggregate", Condition.TRUE)
        self.assertEqual("path.to.Aggregate", qb.aggregate_name)
        self.assertEqual(Condition.TRUE, qb.condition)
        self.assertEqual(None, qb.ordering)
        self.assertEqual(None, qb.limit)

    def test_constructor_full(self):
        qb = PostgreSqlSnapshotQueryBuilder("path.to.Aggregate", Condition.TRUE, Ordering.ASC("name"), 10)
        self.assertEqual("path.to.Aggregate", qb.aggregate_name)
        self.assertEqual(Condition.TRUE, qb.condition)
        self.assertEqual(Ordering.ASC("name"), qb.ordering)
        self.assertEqual(10, qb.limit)

    async def test_build_true(self):
        condition = Condition.TRUE
        observed = PostgreSqlSnapshotQueryBuilder("path.to.Aggregate", condition).build()

        expected_query = (
            "SELECT aggregate_uuid, aggregate_name, version, schema, data, created_at, updated_at "
            "FROM snapshot WHERE (aggregate_name = %(aggregate_name)s) AND (TRUE)"
        )
        expected_parameters = {"aggregate_name": "path.to.Aggregate"}

        self.assertEqual(expected_query, await self._flatten_query(observed[0]))
        self.assertEqual(expected_parameters, self._flatten_parameters(observed[1]))

    async def test_build_false(self):
        condition = Condition.FALSE
        observed = PostgreSqlSnapshotQueryBuilder("path.to.Aggregate", condition).build()
        expected_query = (
            "SELECT aggregate_uuid, aggregate_name, version, schema, data, created_at, updated_at "
            "FROM snapshot WHERE (aggregate_name = %(aggregate_name)s) AND (FALSE)"
        )
        expected_parameters = {"aggregate_name": "path.to.Aggregate"}

        self.assertEqual(expected_query, await self._flatten_query(observed[0]))
        self.assertEqual(expected_parameters, self._flatten_parameters(observed[1]))

    async def test_build_fixed_uuid(self):
        condition = Condition.EQUAL("uuid", 1)
        with patch("minos.common.PostgreSqlSnapshotQueryBuilder.generate_random_str", side_effect=["hello"]):
            observed = PostgreSqlSnapshotQueryBuilder("path.to.Aggregate", condition).build()

        expected_query = (
            "SELECT aggregate_uuid, aggregate_name, version, schema, data, created_at, updated_at "
            'FROM snapshot WHERE (aggregate_name = %(aggregate_name)s) AND (("aggregate_uuid" = %(hello)s))'
        )
        expected_parameters = {"aggregate_name": "path.to.Aggregate", "hello": 1}

        self.assertEqual(expected_query, await self._flatten_query(observed[0]))
        self.assertEqual(expected_parameters, self._flatten_parameters(observed[1]))

    async def test_build_fixed_version(self):
        condition = Condition.EQUAL("version", 1)
        with patch("minos.common.PostgreSqlSnapshotQueryBuilder.generate_random_str", side_effect=["hello"]):
            observed = PostgreSqlSnapshotQueryBuilder("path.to.Aggregate", condition).build()

        expected_query = (
            "SELECT aggregate_uuid, aggregate_name, version, schema, data, created_at, updated_at "
            'FROM snapshot WHERE (aggregate_name = %(aggregate_name)s) AND (("version" = %(hello)s))'
        )
        expected_parameters = {"aggregate_name": "path.to.Aggregate", "hello": 1}

        self.assertEqual(expected_query, await self._flatten_query(observed[0]))
        self.assertEqual(expected_parameters, self._flatten_parameters(observed[1]))

    async def test_build_fixed_created_at(self):
        condition = Condition.EQUAL("created_at", 1)
        with patch("minos.common.PostgreSqlSnapshotQueryBuilder.generate_random_str", side_effect=["hello"]):
            observed = PostgreSqlSnapshotQueryBuilder("path.to.Aggregate", condition).build()

        expected_query = (
            "SELECT aggregate_uuid, aggregate_name, version, schema, data, created_at, updated_at "
            'FROM snapshot WHERE (aggregate_name = %(aggregate_name)s) AND (("created_at" = %(hello)s))'
        )
        expected_parameters = {"aggregate_name": "path.to.Aggregate", "hello": 1}

        self.assertEqual(expected_query, await self._flatten_query(observed[0]))
        self.assertEqual(expected_parameters, self._flatten_parameters(observed[1]))

    async def test_build_fixed_updated_at(self):
        condition = Condition.EQUAL("updated_at", 1)
        with patch("minos.common.PostgreSqlSnapshotQueryBuilder.generate_random_str", side_effect=["hello"]):
            observed = PostgreSqlSnapshotQueryBuilder("path.to.Aggregate", condition).build()

        expected_query = (
            "SELECT aggregate_uuid, aggregate_name, version, schema, data, created_at, updated_at "
            'FROM snapshot WHERE (aggregate_name = %(aggregate_name)s) AND (("updated_at" = %(hello)s))'
        )
        expected_parameters = {"aggregate_name": "path.to.Aggregate", "hello": 1}

        self.assertEqual(expected_query, await self._flatten_query(observed[0]))
        self.assertEqual(expected_parameters, self._flatten_parameters(observed[1]))

    async def test_build_lower(self):
        condition = Condition.LOWER("age", 1)
        with patch("minos.common.PostgreSqlSnapshotQueryBuilder.generate_random_str", side_effect=["hello"]):
            observed = PostgreSqlSnapshotQueryBuilder("path.to.Aggregate", condition).build()

        expected_query = (
            "SELECT aggregate_uuid, aggregate_name, version, schema, data, created_at, updated_at "
            "FROM snapshot "
            "WHERE (aggregate_name = %(aggregate_name)s) AND ((data#>'{age}' < %(hello)s::jsonb))"
        )
        expected_parameters = {"aggregate_name": "path.to.Aggregate", "hello": 1}

        self.assertEqual(expected_query, await self._flatten_query(observed[0]))
        self.assertEqual(expected_parameters, self._flatten_parameters(observed[1]))

    async def test_build_lower_equal(self):
        condition = Condition.LOWER_EQUAL("age", 1)
        with patch("minos.common.PostgreSqlSnapshotQueryBuilder.generate_random_str", side_effect=["hello"]):
            observed = PostgreSqlSnapshotQueryBuilder("path.to.Aggregate", condition).build()

        expected_query = (
            "SELECT aggregate_uuid, aggregate_name, version, schema, data, created_at, updated_at "
            "FROM snapshot "
            "WHERE (aggregate_name = %(aggregate_name)s) AND ((data#>'{age}' <= %(hello)s::jsonb))"
        )
        expected_parameters = {"aggregate_name": "path.to.Aggregate", "hello": 1}

        self.assertEqual(expected_query, await self._flatten_query(observed[0]))
        self.assertEqual(expected_parameters, self._flatten_parameters(observed[1]))

    async def test_build_greater(self):
        condition = Condition.GREATER("age", 1)
        with patch("minos.common.PostgreSqlSnapshotQueryBuilder.generate_random_str", side_effect=["hello"]):
            observed = PostgreSqlSnapshotQueryBuilder("path.to.Aggregate", condition).build()

        expected_query = (
            "SELECT aggregate_uuid, aggregate_name, version, schema, data, created_at, updated_at "
            "FROM snapshot "
            "WHERE (aggregate_name = %(aggregate_name)s) AND ((data#>'{age}' > %(hello)s::jsonb))"
        )
        expected_parameters = {"aggregate_name": "path.to.Aggregate", "hello": 1}

        self.assertEqual(expected_query, await self._flatten_query(observed[0]))
        self.assertEqual(expected_parameters, self._flatten_parameters(observed[1]))

    async def test_build_greater_equal(self):
        condition = Condition.GREATER_EQUAL("age", 1)
        with patch("minos.common.PostgreSqlSnapshotQueryBuilder.generate_random_str", side_effect=["hello"]):
            observed = PostgreSqlSnapshotQueryBuilder("path.to.Aggregate", condition).build()

        expected_query = (
            "SELECT aggregate_uuid, aggregate_name, version, schema, data, created_at, updated_at "
            "FROM snapshot "
            "WHERE (aggregate_name = %(aggregate_name)s) AND ((data#>'{age}' >= %(hello)s::jsonb))"
        )
        expected_parameters = {"aggregate_name": "path.to.Aggregate", "hello": 1}

        self.assertEqual(expected_query, await self._flatten_query(observed[0]))
        self.assertEqual(expected_parameters, self._flatten_parameters(observed[1]))

    async def test_build_equal(self):
        condition = Condition.EQUAL("age", 1)
        with patch("minos.common.PostgreSqlSnapshotQueryBuilder.generate_random_str", side_effect=["hello"]):
            observed = PostgreSqlSnapshotQueryBuilder("path.to.Aggregate", condition).build()

        expected_query = (
            "SELECT aggregate_uuid, aggregate_name, version, schema, data, created_at, updated_at "
            "FROM snapshot "
            "WHERE (aggregate_name = %(aggregate_name)s) AND ((data#>'{age}' = %(hello)s::jsonb))"
        )
        expected_parameters = {"aggregate_name": "path.to.Aggregate", "hello": 1}

        self.assertEqual(expected_query, await self._flatten_query(observed[0]))
        self.assertEqual(expected_parameters, self._flatten_parameters(observed[1]))

    async def test_build_not_equal(self):
        condition = Condition.NOT_EQUAL("age", 1)
        with patch("minos.common.PostgreSqlSnapshotQueryBuilder.generate_random_str", side_effect=["hello"]):
            observed = PostgreSqlSnapshotQueryBuilder("path.to.Aggregate", condition).build()

        expected_query = (
            "SELECT aggregate_uuid, aggregate_name, version, schema, data, created_at, updated_at "
            "FROM snapshot "
            "WHERE (aggregate_name = %(aggregate_name)s) AND ((data#>'{age}' <> %(hello)s::jsonb))"
        )
        expected_parameters = {"aggregate_name": "path.to.Aggregate", "hello": 1}

        self.assertEqual(expected_query, await self._flatten_query(observed[0]))
        self.assertEqual(expected_parameters, self._flatten_parameters(observed[1]))

    async def test_build_in(self):
        condition = Condition.IN("age", {1, 2, 3})
        with patch("minos.common.PostgreSqlSnapshotQueryBuilder.generate_random_str", side_effect=["hello"]):
            observed = PostgreSqlSnapshotQueryBuilder("path.to.Aggregate", condition).build()

        expected_query = (
            "SELECT aggregate_uuid, aggregate_name, version, schema, data, created_at, updated_at "
            "FROM snapshot "
            "WHERE (aggregate_name = %(aggregate_name)s) AND ((data#>'{age}' IN %(hello)s::jsonb))"
        )
        expected_parameters = {"aggregate_name": "path.to.Aggregate", "hello": (1, 2, 3)}

        self.assertEqual(expected_query, await self._flatten_query(observed[0]))
        self.assertEqual(expected_parameters, self._flatten_parameters(observed[1]))

    async def test_build_not(self):
        condition = Condition.NOT(Condition.LOWER("age", 1))
        with patch("minos.common.PostgreSqlSnapshotQueryBuilder.generate_random_str", side_effect=["hello"]):
            observed = PostgreSqlSnapshotQueryBuilder("path.to.Aggregate", condition).build()

        expected_query = (
            "SELECT aggregate_uuid, aggregate_name, version, schema, data, created_at, updated_at "
            "FROM snapshot "
            "WHERE (aggregate_name = %(aggregate_name)s) AND ((NOT (data#>'{age}' < %(hello)s::jsonb)))"
        )
        expected_parameters = {"aggregate_name": "path.to.Aggregate", "hello": 1}

        self.assertEqual(expected_query, await self._flatten_query(observed[0]))
        self.assertEqual(expected_parameters, self._flatten_parameters(observed[1]))

    async def test_build_and(self):
        condition = Condition.AND(Condition.LOWER("age", 1), Condition.LOWER("level", 3))
        with patch("minos.common.PostgreSqlSnapshotQueryBuilder.generate_random_str", side_effect=["hello", "goodbye"]):
            observed = PostgreSqlSnapshotQueryBuilder("path.to.Aggregate", condition).build()

        expected_query = (
            "SELECT aggregate_uuid, aggregate_name, version, schema, data, created_at, updated_at "
            "FROM snapshot "
            "WHERE (aggregate_name = %(aggregate_name)s) AND "
            "(((data#>'{age}' < %(hello)s::jsonb) AND (data#>'{level}' < %(goodbye)s::jsonb)))"
        )
        expected_parameters = {"aggregate_name": "path.to.Aggregate", "hello": 1, "goodbye": 3}

        self.assertEqual(expected_query, await self._flatten_query(observed[0]))
        self.assertEqual(expected_parameters, self._flatten_parameters(observed[1]))

    async def test_build_or(self):
        condition = Condition.OR(Condition.LOWER("age", 1), Condition.LOWER("level", 3))
        with patch("minos.common.PostgreSqlSnapshotQueryBuilder.generate_random_str", side_effect=["hello", "goodbye"]):
            observed = PostgreSqlSnapshotQueryBuilder("path.to.Aggregate", condition).build()

        expected_query = (
            "SELECT aggregate_uuid, aggregate_name, version, schema, data, created_at, updated_at "
            "FROM snapshot "
            "WHERE (aggregate_name = %(aggregate_name)s) AND "
            "(((data#>'{age}' < %(hello)s::jsonb) OR (data#>'{level}' < %(goodbye)s::jsonb)))"
        )
        expected_parameters = {"aggregate_name": "path.to.Aggregate", "hello": 1, "goodbye": 3}

        self.assertEqual(expected_query, await self._flatten_query(observed[0]))
        self.assertEqual(expected_parameters, self._flatten_parameters(observed[1]))

    async def test_build_fixed_ordering_asc(self):
        ordering = Ordering.ASC("created_at")
        observed = PostgreSqlSnapshotQueryBuilder("path.to.Aggregate", Condition.TRUE, ordering).build()

        # noinspection SqlRedundantOrderingDirection
        expected_query = (
            "SELECT aggregate_uuid, aggregate_name, version, schema, data, created_at, updated_at "
            "FROM snapshot "
            "WHERE (aggregate_name = %(aggregate_name)s) AND (TRUE) "
            'ORDER BY "created_at" ASC'
        )
        expected_parameters = {"aggregate_name": "path.to.Aggregate"}

        self.assertEqual(expected_query, await self._flatten_query(observed[0]))
        self.assertEqual(expected_parameters, self._flatten_parameters(observed[1]))

    async def test_build_fixed_ordering_desc(self):
        ordering = Ordering.DESC("created_at")
        observed = PostgreSqlSnapshotQueryBuilder("path.to.Aggregate", Condition.TRUE, ordering).build()

        expected_query = (
            "SELECT aggregate_uuid, aggregate_name, version, schema, data, created_at, updated_at "
            "FROM snapshot "
            "WHERE (aggregate_name = %(aggregate_name)s) AND (TRUE) "
            'ORDER BY "created_at" DESC'
        )
        expected_parameters = {"aggregate_name": "path.to.Aggregate"}

        self.assertEqual(expected_query, await self._flatten_query(observed[0]))
        self.assertEqual(expected_parameters, self._flatten_parameters(observed[1]))

    async def test_build_ordering_asc(self):
        ordering = Ordering.ASC("name")
        observed = PostgreSqlSnapshotQueryBuilder("path.to.Aggregate", Condition.TRUE, ordering).build()

        # noinspection SqlRedundantOrderingDirection
        expected_query = (
            "SELECT aggregate_uuid, aggregate_name, version, schema, data, created_at, updated_at "
            "FROM snapshot "
            "WHERE (aggregate_name = %(aggregate_name)s) AND (TRUE) "
            "ORDER BY data#>'{name}' ASC"
        )
        expected_parameters = {"aggregate_name": "path.to.Aggregate"}

        self.assertEqual(expected_query, await self._flatten_query(observed[0]))
        self.assertEqual(expected_parameters, self._flatten_parameters(observed[1]))

    async def test_build_ordering_desc(self):
        ordering = Ordering.DESC("name")
        observed = PostgreSqlSnapshotQueryBuilder("path.to.Aggregate", Condition.TRUE, ordering).build()

        expected_query = (
            "SELECT aggregate_uuid, aggregate_name, version, schema, data, created_at, updated_at "
            "FROM snapshot "
            "WHERE (aggregate_name = %(aggregate_name)s) AND (TRUE) "
            "ORDER BY data#>'{name}' DESC"
        )
        expected_parameters = {"aggregate_name": "path.to.Aggregate"}

        self.assertEqual(expected_query, await self._flatten_query(observed[0]))
        self.assertEqual(expected_parameters, self._flatten_parameters(observed[1]))

    async def test_build_limit(self):
        observed = PostgreSqlSnapshotQueryBuilder("path.to.Aggregate", Condition.TRUE, limit=10).build()

        expected_query = (
            "SELECT aggregate_uuid, aggregate_name, version, schema, data, created_at, updated_at "
            "FROM snapshot "
            "WHERE (aggregate_name = %(aggregate_name)s) AND (TRUE) "
            "LIMIT 10"
        )
        expected_parameters = {"aggregate_name": "path.to.Aggregate"}

        self.assertEqual(expected_query, await self._flatten_query(observed[0]))
        self.assertEqual(expected_parameters, self._flatten_parameters(observed[1]))

    async def test_build_complex(self):
        condition = Condition.AND(
            Condition.EQUAL("inventory.amount", 0),
            Condition.OR(Condition.EQUAL("title", "Fanta Zero"), Condition.GREATER("version", 1)),
        )
        ordering = Ordering.DESC("updated_at")
        limit = 100

        with patch(
            "minos.common.PostgreSqlSnapshotQueryBuilder.generate_random_str", side_effect=["one", "two", "three"]
        ):
            observed = PostgreSqlSnapshotQueryBuilder("path.to.Aggregate", condition, ordering, limit).build()

        expected_query = (
            "SELECT aggregate_uuid, aggregate_name, version, schema, data, created_at, updated_at "
            "FROM snapshot "
            "WHERE (aggregate_name = %(aggregate_name)s) AND "
            "(((data#>'{inventory,amount}' = %(one)s::jsonb) AND ((data#>'{title}' = %(two)s::jsonb) OR "
            '("version" > %(three)s)))) '
            'ORDER BY "updated_at" DESC '
            "LIMIT 100"
        )
        expected_parameters = {"aggregate_name": "path.to.Aggregate", "one": 0, "three": 1, "two": "Fanta Zero"}

        self.assertEqual(expected_query, await self._flatten_query(observed[0]))
        self.assertEqual(expected_parameters, self._flatten_parameters(observed[1]))

    async def _flatten_query(self, query) -> str:
        async with aiopg.connect(**self.snapshot_db) as connection:
            return query.as_string(connection.raw)

    @staticmethod
    def _flatten_parameters(parameters) -> dict:
        return {k: (v if not isinstance(v, Json) else v.adapted) for k, v in parameters.items()}


if __name__ == "__main__":
    unittest.main()
