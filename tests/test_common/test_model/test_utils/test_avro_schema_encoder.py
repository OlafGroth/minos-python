"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""

import unittest
from datetime import (
    date,
    datetime,
    time,
)
from typing import (
    Optional,
)
from uuid import (
    UUID,
)

from minos.common import (
    AvroSchemaEncoder,
    ModelRef,
    ModelType,
)
from tests.aggregate_classes import (
    Owner,
)
from tests.model_classes import (
    User,
)


class TestAvroSchemaEncoder(unittest.TestCase):
    def test_model_type(self):
        expected = {
            "name": "class",
            "type": {
                "fields": [{"name": "username", "type": "string"}],
                "name": "User",
                "namespace": "path.to.class",
                "type": "record",
            },
        }

        observed = AvroSchemaEncoder("class", ModelType.build("User", {"username": str}, "path.to")).build()
        self.assertEqual(expected, observed)

    def test_avro_schema_int(self):
        observed = AvroSchemaEncoder("test", int).build()
        expected = {"name": "test", "type": "int"}
        self.assertEqual(expected, observed)

    def test_avro_schema_bool(self):
        expected = {"name": "test", "type": "boolean"}
        observed = AvroSchemaEncoder("test", bool).build()
        self.assertEqual(expected, observed)

    def test_avro_schema_float(self):
        expected = {"name": "test", "type": "double"}
        observed = AvroSchemaEncoder("test", float).build()
        self.assertEqual(expected, observed)

    def test_avro_schema_string(self):
        expected = {"name": "test", "type": "string"}
        observed = AvroSchemaEncoder("test", str).build()
        self.assertEqual(expected, observed)

    def test_avro_schema_bytes(self):
        expected = {"name": "test", "type": "bytes"}
        observed = AvroSchemaEncoder("test", bytes).build()
        self.assertEqual(expected, observed)

    def test_avro_schema_date(self):
        expected = {"name": "test", "type": {"type": "int", "logicalType": "date"}}
        observed = AvroSchemaEncoder("test", date).build()
        self.assertEqual(expected, observed)

    def test_avro_schema_time(self):
        expected = {"name": "test", "type": {"type": "int", "logicalType": "time-micros"}}
        observed = AvroSchemaEncoder("test", time).build()
        self.assertEqual(expected, observed)

    def test_avro_schema_datetime(self):
        expected = {"name": "test", "type": {"type": "long", "logicalType": "timestamp-micros"}}
        observed = AvroSchemaEncoder("test", datetime).build()
        self.assertEqual(expected, observed)

    def test_avro_schema_dict(self):
        expected = {"name": "test", "type": {"type": "map", "values": "int"}}
        observed = AvroSchemaEncoder("test", dict[str, int]).build()
        self.assertEqual(expected, observed)

    def test_avro_schema_model_ref(self):
        expected = {
            "name": "test",
            "type": [
                {
                    "fields": [
                        {"name": "id", "type": "int"},
                        {"name": "version", "type": "int"},
                        {"name": "name", "type": "string"},
                        {"name": "surname", "type": "string"},
                        {"name": "age", "type": ["int", "null"]},
                    ],
                    "name": "Owner",
                    "namespace": "tests.aggregate_classes.test",
                    "type": "record",
                },
                "int",
                "null",
            ],
        }
        observed = AvroSchemaEncoder("test", Optional[ModelRef[Owner]]).build()
        self.assertEqual(expected, observed)

    def test_avro_schema_list_model(self):
        expected = {
            "name": "test",
            "type": {
                "items": [
                    {
                        "fields": [{"name": "id", "type": "int"}, {"name": "username", "type": ["string", "null"]}],
                        "name": "User",
                        "namespace": "tests.model_classes.test",
                        "type": "record",
                    },
                    "null",
                ],
                "type": "array",
            },
        }
        observed = AvroSchemaEncoder("test", list[Optional[User]]).build()
        self.assertEqual(expected, observed)

    def test_avro_schema_uuid(self):
        expected = {"name": "test", "type": {"type": "string", "logicalType": "uuid"}}
        observed = AvroSchemaEncoder("test", UUID).build()
        self.assertEqual(expected, observed)


if __name__ == "__main__":
    unittest.main()
