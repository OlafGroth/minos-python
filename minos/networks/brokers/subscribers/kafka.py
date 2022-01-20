from __future__ import annotations

import logging
from contextlib import suppress

from aiokafka import (
    AIOKafkaConsumer,
    ConsumerRecord,
)
from cached_property import cached_property
from kafka import KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError

from minos.common import MinosConfig

from ..messages import BrokerMessage
from .abc import BrokerSubscriber

logger = logging.getLogger(__name__)


class KafkaBrokerSubscriber(BrokerSubscriber):
    """TODO"""

    def __init__(
        self, *args, broker_host: str, broker_port: int, group_id: str, remove_topics_on_destroy: bool = False, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.group_id = group_id

        self.remove_topics_on_destroy = remove_topics_on_destroy

    @classmethod
    def _from_config(cls, config: MinosConfig, **kwargs) -> KafkaBrokerSubscriber:
        if "group_id" not in kwargs:
            kwargs["group_id"] = config.service.name
        return cls(broker_host=config.broker.host, broker_port=config.broker.port, **kwargs)

    async def _setup(self) -> None:
        await super()._setup()
        for topic in self.topics:
            self._create_topic(topic)

        await self.client.start()

    async def _destroy(self) -> None:
        await self.client.stop()

        if self.remove_topics_on_destroy:
            for topic in self.topics:
                self._delete_topic(topic)
        self.admin_client.close()

        await super()._destroy()

    def _create_topic(self, topic: str) -> None:
        logger.info(f"Creating {topic!r} topic...")
        with suppress(TopicAlreadyExistsError):
            self.admin_client.create_topics([NewTopic(name=topic, num_partitions=1, replication_factor=1)])

    def _delete_topic(self, topic: str) -> None:
        logger.info(f"Deleting {topic!r} topic...")
        self.admin_client.delete_topics([topic])

    @cached_property
    def admin_client(self):
        """TODO

        :return: TODO
        """
        return KafkaAdminClient(bootstrap_servers=f"{self.broker_host}:{self.broker_port}")

    async def receive(self) -> BrokerMessage:
        """TODO

        :return: TODO

        """
        record = await self.client.getone()
        return self._dispatch_one(record)

    @staticmethod
    def _dispatch_one(record: ConsumerRecord) -> BrokerMessage:
        bytes_ = record.value
        message = BrokerMessage.from_avro_bytes(bytes_)
        logger.info(f"Consuming {message!r} message...")
        return message

    @cached_property
    def client(self) -> AIOKafkaConsumer:
        """Get the kafka consumer client.

        :return: An ``AIOKafkaConsumer`` instance.
        """
        return AIOKafkaConsumer(
            *self._topics,
            bootstrap_servers=f"{self.broker_host}:{self.broker_port}",
            group_id=self.group_id,
            auto_offset_reset="earliest",
        )
