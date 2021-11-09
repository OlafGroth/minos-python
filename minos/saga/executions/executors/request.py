from __future__ import (
    annotations,
)

from typing import (
    Optional,
)
from uuid import (
    UUID,
)

from dependency_injector.wiring import (
    Provide,
    inject,
)

from minos.common import (
    MinosBroker,
    NotProvidedException,
)

from ...context import (
    SagaContext,
)
from ...definitions import (
    RequestCallBack,
    SagaOperation,
)
from ...exceptions import (
    ExecutorException,
    SagaFailedExecutionStepException,
)
from ...messages import (
    SagaRequest,
)
from .abc import (
    Executor,
)


class RequestExecutor(Executor):
    """Request class.

    This class has the responsibility to publish command on the corresponding broker's queue.
    """

    @inject
    def __init__(
        self,
        *args,
        reply_topic: Optional[str],
        user: Optional[UUID],
        command_broker: MinosBroker = Provide["command_broker"],
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.reply_topic = reply_topic
        self.user = user

        if command_broker is None or isinstance(command_broker, Provide):
            raise NotProvidedException("A broker instance is required.")

        self.command_broker = command_broker

    # noinspection PyMethodOverriding
    async def exec(self, operation: Optional[SagaOperation[RequestCallBack]], context: SagaContext) -> SagaContext:
        """Exec method, that perform the publishing logic run an pre-callback function to generate the command contents.

        :param operation: Operation to be executed.
        :param context: Execution context.
        :return: A saga context instance.
        """
        if operation is None:
            return context

        try:
            context = SagaContext(**context)  # Needed to avoid mutability issues.
            request = await super().exec(operation, context)
            await self._publish(request)
        except ExecutorException as exc:
            raise SagaFailedExecutionStepException(exc.exception)
        return context

    async def _publish(self, request: SagaRequest) -> None:
        fn = self.command_broker.send
        topic = request.target
        data = await request.content()
        saga = self.execution_uuid
        reply_topic = self.reply_topic
        user = self.user
        await self.exec_function(fn, topic=topic, data=data, saga=saga, reply_topic=reply_topic, user=user)
