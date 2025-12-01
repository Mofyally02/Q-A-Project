"""
RabbitMQ queue utilities
Async queue management for background tasks
"""

import json
import logging
from typing import Any, Dict, Optional, Callable

try:
    import aio_pika
    from aio_pika.abc import AbstractConnection, AbstractChannel, AbstractQueue
    AIO_PIKA_AVAILABLE = True
except ImportError:
    AIO_PIKA_AVAILABLE = False
    AbstractConnection = None
    AbstractChannel = None
    AbstractQueue = None

from app.core.config import settings

logger = logging.getLogger(__name__)


class QueueService:
    """RabbitMQ queue service with async support"""
    
    def __init__(self):
        self.connection: Optional[AbstractConnection] = None
        self.channel: Optional[AbstractChannel] = None
        self._queues: Dict[str, AbstractQueue] = {}
    
    async def connect(self):
        """Initialize RabbitMQ connection"""
        if not AIO_PIKA_AVAILABLE:
            logger.warning("aio-pika not installed. RabbitMQ features will be disabled.")
            return
        
        try:
            connection_url = (
                f"amqp://{settings.rabbitmq_user}:{settings.rabbitmq_password}"
                f"@{settings.rabbitmq_host}:{settings.rabbitmq_port}{settings.rabbitmq_vhost}"
            )
            self.connection = await aio_pika.connect_robust(connection_url)
            self.channel = await self.connection.channel()
            logger.info("RabbitMQ connection established")
        except Exception as e:
            logger.warning(f"RabbitMQ connection failed: {e}. Continuing without queue service.")
            self.connection = None
            self.channel = None
    
    async def disconnect(self):
        """Close RabbitMQ connection"""
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()
        logger.info("RabbitMQ connection closed")
    
    async def declare_queue(self, queue_name: str, durable: bool = True) -> AbstractQueue:
        """Declare a queue (create if doesn't exist)"""
        if not self.channel:
            raise RuntimeError("Queue service not connected")
        
        if queue_name not in self._queues:
            queue = await self.channel.declare_queue(
                queue_name,
                durable=durable
            )
            self._queues[queue_name] = queue
            logger.info(f"Queue declared: {queue_name}")
        
        return self._queues[queue_name]
    
    async def publish(self, queue_name: str, message: Dict[str, Any], durable: bool = True):
        """Publish message to queue"""
        if not AIO_PIKA_AVAILABLE:
            logger.warning("aio-pika not available. Message not published.")
            return
        
        if not self.channel:
            raise RuntimeError("Queue service not connected")
        
        queue = await self.declare_queue(queue_name, durable)
        
        message_body = json.dumps(message).encode()
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=message_body,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT if durable else None
            ),
            routing_key=queue_name
        )
        logger.debug(f"Message published to {queue_name}")
    
    async def consume(
        self,
        queue_name: str,
        callback: Callable[[Dict[str, Any]], None],
        durable: bool = True
    ):
        """Consume messages from queue"""
        if not self.channel:
            raise RuntimeError("Queue service not connected")
        
        queue = await self.declare_queue(queue_name, durable)
        
        async def process_message(message: aio_pika.IncomingMessage):
            async with message.process():
                try:
                    body = json.loads(message.body.decode())
                    await callback(body)
                except Exception as e:
                    logger.error(f"Error processing message from {queue_name}: {e}")
                    # Message will be requeued if not acknowledged
        
        await queue.consume(process_message)
        logger.info(f"Started consuming from queue: {queue_name}")


# Global queue service instance
queue_service = QueueService()

