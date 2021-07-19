"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""
import unittest

from minos.networks import (
    FindDecorators,
    enroute,
)


class RestQueryExample:
    @enroute.rest.query(url="tickets/", method="GET")
    def get_tickets(self):
        return "tickets"

    def bar(self):
        return "bar"


class RestCommandExample:
    @enroute.rest.command(topics=["RestCommand"])
    def get_tickets(self):
        return "tickets"

    def bar(self):
        return "bar"


class BrokerQueryExample:
    @enroute.broker.query(topics=["BrokerQuery"])
    def get_tickets(self):
        return "tickets"

    def bar(self):
        return "bar"


class BrokerCommandExample:
    @enroute.broker.command(topics=["BrokerCommand"])
    def get_tickets(self):
        return "tickets"

    def bar(self):
        return "bar"


class BrokerEventExample:
    @enroute.broker.event(topics=["BrokerEvent"])
    def get_tickets(self):
        return "tickets"

    def bar(self):
        return "bar"


def decorated_func():
    return "test"


class TestDecorators(unittest.IsolatedAsyncioTestCase):
    async def test_rest_query_base(self):
        func = enroute.rest.query(url="tickets/", method="GET")
        wrapper = func(decorated_func)
        result = wrapper()
        self.assertEqual("test", result)

    async def test_rest_query_decorator(self):
        result = FindDecorators.find_inside_class(RestQueryExample)

        self.assertEqual("GET", result[0].method)
        self.assertEqual("tickets/", result[0].url)

    async def test_rest_command(self):
        func = enroute.rest.command(topics=["CreateTicket"])
        wrapper = func(decorated_func)
        result = wrapper()
        self.assertEqual("test", result)

    async def test_rest_command_decorator(self):
        result = FindDecorators.find_inside_class(RestCommandExample)

        self.assertEqual(["RestCommand"], result[0]["topics"])

    async def test_broker_query(self):
        func = enroute.broker.query(topics=["CreateTicket"])
        wrapper = func(decorated_func)
        result = wrapper()
        self.assertEqual("test", result)

    async def test_broker_query_decorator(self):
        result = FindDecorators.find_inside_class(BrokerQueryExample)

        self.assertEqual(["BrokerQuery"], result[0]["topics"])

    async def test_broker_command(self):
        func = enroute.broker.command(topics=["CreateTicket"])
        wrapper = func(decorated_func)
        result = wrapper()
        self.assertEqual("test", result)

    async def test_broker_command_decorator(self):
        result = FindDecorators.find_inside_class(BrokerCommandExample)

        self.assertEqual(["BrokerCommand"], result[0]["topics"])

    async def test_broker_event(self):
        func = enroute.broker.event(topics=["CreateTicket"])
        wrapper = func(decorated_func)
        result = wrapper()
        self.assertEqual("test", result)

    async def test_broker_event_decorator(self):
        result = FindDecorators.find_inside_class(BrokerEventExample)

        self.assertEqual(["BrokerEvent"], result[0]["topics"])


if __name__ == "__main__":
    unittest.main()
