"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""
from __future__ import (
    annotations,
)

import logging
from uuid import (
    UUID,
)

from minos.common import (
    CommandReply,
    MinosConfig,
    MinosSagaManager,
    import_module,
)

from .definitions import (
    Saga,
)
from .exceptions import (
    MinosSagaFailedExecutionStepException,
    MinosSagaPausedExecutionStepException,
)
from .executions import (
    SagaExecution,
    SagaExecutionStorage,
)

logger = logging.getLogger(__name__)


def _build_definitions(items) -> dict[str, Saga]:
    def _fn(item) -> Saga:
        controller = import_module(item.controller)
        return getattr(controller, item.action)

    return {item.name: _fn(item) for item in items}


class SagaManager(MinosSagaManager):
    """Saga Manager implementation class.

    The purpose of this class is to manage the running process for new or paused``SagaExecution`` instances.
    """

    # noinspection PyUnusedLocal
    def __init__(self, storage: SagaExecutionStorage, definitions: dict[str, Saga], *args, **kwargs):
        self.storage = storage
        self.definitions = definitions

    @classmethod
    def from_config(cls, *args, config: MinosConfig = None, **kwargs) -> MinosSagaManager:
        """Build an instance from config.

        :param args: Additional positional arguments.
        :param config: Config instance.
        :param kwargs: Additional named arguments.
        :return: A new ``classmethod`` instance.
        """
        storage = SagaExecutionStorage.from_config(config=config, **kwargs)
        definitions = _build_definitions(config.saga.items)
        return cls(*args, storage=storage, definitions=definitions, **kwargs)

    async def run(self, name=None, reply=None, **kwargs):
        """Perform a run of a ``Saga``.

        The run can be a new one (if a name is provided) or continue execution a previous one (if a reply is provided).

        :param name: The name of the saga to be executed.
        :param reply: The reply that relaunches a saga execution.
        :param kwargs: Additional named arguments.
        :return: This method does not return anything.
        """
        if name is not None:
            return await self._run_new(name, **kwargs)

        if reply is not None:
            return await self._load_and_run(reply, **kwargs)

        raise ValueError("At least a 'name' or a 'reply' must be provided.")

    async def _run_new(self, name: str, **kwargs) -> UUID:
        definition = self.definitions.get(name)
        execution = SagaExecution.from_saga(definition)
        return await self._run(execution, **kwargs)

    async def _load_and_run(self, reply: CommandReply, **kwargs) -> UUID:
        execution = self.storage.load(reply.task_id)
        return await self._run(execution, reply=reply, **kwargs)

    async def _run(self, execution: SagaExecution, **kwargs) -> UUID:
        try:
            await execution.execute(**kwargs)
        except MinosSagaPausedExecutionStepException:
            self.storage.store(execution)
            return execution.uuid
        except MinosSagaFailedExecutionStepException:
            logger.warning(f"The execution identified by {execution.uuid} failed.")
            self.storage.store(execution)
            return execution.uuid

        self.storage.delete(execution)
        return execution.uuid
