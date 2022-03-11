from minos.networks import (
    Request,
    Response,
    enroute,
)


class QueryService:
    @enroute.rest.query(url="/ticket", method="POST")
    def add_ticket(self, request: Request) -> Response:
        return Response("ticket_added")

    @enroute.broker.event("TicketAdded")
    def ticket_added(self, request: Request):
        return "query_service_ticket_added"

    @enroute.broker.event("TicketDeleted")
    def ticket_deleted(self, request: Request):
        return "ticket_deleted"
