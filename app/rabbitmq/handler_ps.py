import asyncio
import aioamqp
from .connection import RabbitMQ
from .constants import RABBITMQ_QUEUE
from ..utils.file_handler import write_to_file


async def send_message(message: str):
    channel = RabbitMQ._channel

    await channel.basic_publish(
        payload=message.encode(), exchange_name="", routing_key=RABBITMQ_QUEUE
    )


async def callback(channel, body, delivery_tag):
    # Process message
    print(body, delivery_tag)
    write_to_file(body)
    # Acknowledge message
    await channel.basic_client_ack(delivery_tag)
    print(f"Acknowledged message with delivery tag {delivery_tag}")


async def consume_message():
    protocol = RabbitMQ._protocol

    channel = RabbitMQ._channel

    # Set prefetch count to control message delivery rate
    await channel.basic_qos(prefetch_count=1)
    # Start consuming messages indefinitely
    while True:
        try:
            if protocol is None:
                print("protocol is empty")
                await RabbitMQ.get_connection()
                protocol = RabbitMQ._protocol
                channel = RabbitMQ._channel
            message = await channel.basic_get(RABBITMQ_QUEUE, no_ack=False)

            if message is None:
                await asyncio.sleep(1)  # Wait before checking for new messages
                continue

            body = message["message"].decode("utf-8")
            delivery_tag = message["delivery_tag"]

            await callback(channel, body, delivery_tag)

        except aioamqp.exceptions.EmptyQueue:
            # If queue is empty, wait and continue
            print("EMpty Queue")
            await asyncio.sleep(1)
            continue

        except aioamqp.exceptions.ChannelClosed:
            await asyncio.sleep(5)  # Wait before attempting to reconnect
            RabbitMQ.close()
            protocol = None
            print("Closed channel")
            continue

        except aioamqp.exceptions.AmqpClosedConnection:
            await asyncio.sleep(5)  # Wait before attempting to reconnect
            protocol = None
            print("Connection closed unexpectedly")
            continue


async def publish_message(message: str):
    await send_message(message)


# Using asyncio.create_task for Python 3.7+
