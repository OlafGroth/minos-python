import unittest

from minos.common import (
    classname,
)
from minos.networks import (
    BrokerCommandEnrouteDecorator,
    BrokerEventEnrouteDecorator,
    BrokerQueryEnrouteDecorator,
    EnrouteAnalyzer,
    GraphqlQueryEnrouteDecorator,
    PeriodicEventEnrouteDecorator,
    RestCommandEnrouteDecorator,
    RestQueryEnrouteDecorator,
)
from tests.utils import (
    FakeService,
    FakeServiceWithGetEnroute,
)


class TestEnrouteAnalyzer(unittest.IsolatedAsyncioTestCase):
    def test_decorated_str(self):
        analyzer = EnrouteAnalyzer(classname(FakeService))
        self.assertEqual(FakeService, analyzer.decorated)

    def test_get_all(self):
        analyzer = EnrouteAnalyzer(FakeService)

        observed = analyzer.get_all()
        expected = {
            "get_tickets": {BrokerQueryEnrouteDecorator("GetTickets"), RestQueryEnrouteDecorator("tickets/", "GET")},
            "create_ticket": {
                BrokerCommandEnrouteDecorator("CreateTicket"),
                BrokerCommandEnrouteDecorator("AddTicket"),
                RestCommandEnrouteDecorator("orders/", "GET"),
            },
            "ticket_added": {BrokerEventEnrouteDecorator("TicketAdded")},
            "delete_ticket": {
                BrokerCommandEnrouteDecorator("DeleteTicket"),
                RestCommandEnrouteDecorator("orders/", "DELETE"),
            },
            "send_newsletter": {PeriodicEventEnrouteDecorator("@daily")},
            "check_inactive_users": {PeriodicEventEnrouteDecorator("@daily")},
            "graphql_handler": {GraphqlQueryEnrouteDecorator("graphql/", "GET")},
            "graphql_handler2": {GraphqlQueryEnrouteDecorator("graphql-2/", "GET")},
            "graphql_handler3": {GraphqlQueryEnrouteDecorator("graphql-3/", "POST")},
        }

        self.assertEqual(expected, observed)

    def test_get_rest_command_query(self):
        analyzer = EnrouteAnalyzer(FakeService)

        observed = analyzer.get_rest_command_query()
        expected = {
            "get_tickets": {RestQueryEnrouteDecorator("tickets/", "GET")},
            "create_ticket": {RestCommandEnrouteDecorator("orders/", "GET")},
            "delete_ticket": {RestCommandEnrouteDecorator("orders/", "DELETE")},
        }

        self.assertEqual(expected, observed)

    def test_get_graphql(self):
        analyzer = EnrouteAnalyzer(FakeService)

        observed = analyzer.get_graphql()
        expected = {
            "graphql_handler": {GraphqlQueryEnrouteDecorator("graphql/", "GET")},
            "graphql_handler2": {GraphqlQueryEnrouteDecorator("graphql-2/", "GET")},
            "graphql_handler3": {GraphqlQueryEnrouteDecorator("graphql-3/", "POST")},
        }

        self.assertEqual(expected, observed)

    def test_get_broker_command_query_event(self):
        analyzer = EnrouteAnalyzer(FakeService)

        observed = analyzer.get_broker_command_query_event()
        expected = {
            "get_tickets": {BrokerQueryEnrouteDecorator("GetTickets")},
            "create_ticket": {
                BrokerCommandEnrouteDecorator("CreateTicket"),
                BrokerCommandEnrouteDecorator("AddTicket"),
            },
            "delete_ticket": {BrokerCommandEnrouteDecorator("DeleteTicket")},
            "ticket_added": {BrokerEventEnrouteDecorator("TicketAdded")},
        }

        self.assertEqual(expected, observed)

    def test_get_broker_command_query(self):
        analyzer = EnrouteAnalyzer(FakeService)

        observed = analyzer.get_broker_command_query()
        expected = {
            "get_tickets": {BrokerQueryEnrouteDecorator("GetTickets")},
            "create_ticket": {
                BrokerCommandEnrouteDecorator("CreateTicket"),
                BrokerCommandEnrouteDecorator("AddTicket"),
            },
            "delete_ticket": {BrokerCommandEnrouteDecorator("DeleteTicket")},
        }

        self.assertEqual(expected, observed)

    def test_get_broker_event(self):
        analyzer = EnrouteAnalyzer(FakeService)

        observed = analyzer.get_broker_event()
        expected = {"ticket_added": {BrokerEventEnrouteDecorator("TicketAdded")}}

        self.assertEqual(expected, observed)

    def test_get_periodic_event(self):
        analyzer = EnrouteAnalyzer(FakeService)

        observed = analyzer.get_periodic_event()
        expected = {
            "send_newsletter": {PeriodicEventEnrouteDecorator("@daily")},
            "check_inactive_users": {PeriodicEventEnrouteDecorator("@daily")},
        }

        self.assertEqual(expected, observed)

    def test_with_get_enroute(self):
        analyzer = EnrouteAnalyzer(FakeServiceWithGetEnroute)

        observed = analyzer.get_all()
        expected = {"create_foo": {BrokerCommandEnrouteDecorator("CreateFoo")}}

        self.assertEqual(expected, observed)


if __name__ == "__main__":
    unittest.main()
