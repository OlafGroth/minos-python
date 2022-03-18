import typing as t
import unittest
from asyncio import (
    gather,
    sleep,
)
from unittest.mock import (
    MagicMock,
)

from aiomisc import (
    PoolBase,
)
from aiomisc.pool import (
    T,
)

from minos.common import (
    MinosPool,
    SetupMixin,
)


class _Pool(MinosPool):
    def __init__(self):
        super().__init__()
        self.create_instance_call_count = 0
        self.destroy_instance_call_count = 0

    async def _create_instance(self) -> T:
        self.create_instance_call_count += 1
        return "foo"

    async def _destroy_instance(self, instance: t.Any) -> None:
        self.destroy_instance_call_count += 1


class TestMinosPool(unittest.IsolatedAsyncioTestCase):
    def test_abstract(self):
        self.assertTrue(issubclass(MinosPool, (SetupMixin, PoolBase)))
        # noinspection PyUnresolvedReferences
        self.assertEqual({"_destroy_instance", "_create_instance"}, MinosPool.__abstractmethods__)

    async def test_acquire(self):
        async with _Pool() as pool:
            self.assertEqual(0, pool.create_instance_call_count)
            self.assertEqual(0, pool.destroy_instance_call_count)
            async with pool.acquire() as observed:
                self.assertEqual(1, pool.create_instance_call_count)
                self.assertEqual(0, pool.destroy_instance_call_count)
                self.assertEqual("foo", observed)
        self.assertEqual(1, pool.create_instance_call_count)
        self.assertLess(0, pool.destroy_instance_call_count)

    async def test_close(self):
        async def _fn1(p):
            async with p.acquire():
                await sleep(0.5)

        async def _fn2(p):
            await p.destroy()

        async with _Pool() as pool:
            pool_mock = MagicMock(side_effect=pool.close)
            pool.close = pool_mock
            await gather(_fn1(pool), _fn2(pool))

        self.assertEqual(1, pool_mock.call_count)


if __name__ == "__main__":
    unittest.main()
