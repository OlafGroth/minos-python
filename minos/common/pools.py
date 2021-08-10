"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""
from __future__ import (
    annotations,
)

from abc import (
    ABC,
)
from typing import (
    NoReturn,
    Optional,
    TypeVar,
)

from aiomisc import (
    PoolBase,
)

from .setup import (
    MinosSetup,
)


class MinosPool(MinosSetup, PoolBase, ABC):
    """Base class for Pool implementations in minos"""

    def __init__(self, *args, maxsize: int = 10, recycle: Optional[int] = None, already_setup: bool = True, **kwargs):
        MinosSetup.__init__(self, *args, already_setup=already_setup, **kwargs)
        PoolBase.__init__(self, maxsize=maxsize, recycle=recycle)

    def acquire(self) -> T:
        """Acquire a new instance wrapped on an asynchronous context manager.

        :return: An asynchronous context manager.
        """
        return super().acquire()

    async def _destroy(self) -> NoReturn:
        await self.close()

    async def _check_instance(self: T, instance: T) -> bool:
        return True


T = TypeVar("T")
