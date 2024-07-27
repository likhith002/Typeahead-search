import os
from aioamqp import connect
from .constants import (
    RABBITMQ_HOST,
    RABBITMQ_DEFAULT_PASS,
    RABBITMQ_PORT,
    RABBITMQ_QUEUE,
    RABBITMQ_DEFAULT_USER,
)


class RabbitMQ:
    _transport = None
    _protocol = None
    _channel = None
    _connected = False

    @classmethod
    async def get_connection(cls):
        if cls._connected is False:
            cls._connected = True
            cls._transport, cls._protocol = await connect(
                host=RABBITMQ_HOST,
                port=os.getenv("RABBITMQ_PORT") or RABBITMQ_PORT,
                login=os.getenv("RABBITMQ_DEFAULT_USER") or RABBITMQ_DEFAULT_USER,
                password=os.getenv("RABBITMQ_DEFAULT_PASS") or RABBITMQ_DEFAULT_PASS,
            )
            cls._channel = await cls._protocol.channel()
            await cls._channel.queue_declare(queue_name=RABBITMQ_QUEUE, durable=True)

        return cls._transport, cls._protocol

    @classmethod
    async def close(cls):
        cls._connected = False
        if cls._protocol:
            await cls._protocol.close()
        if cls._transport:
            cls._transport.close()
