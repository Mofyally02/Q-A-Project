import asyncio
import json
import logging
import pika
from typing import Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

class QueueService:
    def __init__(self):
        self.connection = None
        self.channel = None
    
    async def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(settings.rabbitmq_user, settings.rabbitmq_password)
            parameters = pika.ConnectionParameters(
                host=settings.rabbitmq_host,
                port=settings.rabbitmq_port,
                credentials=credentials
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare queues
            self._declare_queues()
            
            logger.info("Connected to RabbitMQ successfully")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    def _declare_queues(self):
        """Declare all required queues"""
        queues = [
            "ai_processing",
            "humanization",
            "originality_check",
            "expert_review",
            "delivery",
            "notification"
        ]
        
        for queue in queues:
            self.channel.queue_declare(queue=queue, durable=True)
    
    async def enqueue_ai_processing(self, question_id: str):
        """Enqueue question for AI processing"""
        await self._enqueue_task("ai_processing", {"question_id": question_id})
    
    async def enqueue_humanization(self, answer_id: str):
        """Enqueue answer for humanization"""
        await self._enqueue_task("humanization", {"answer_id": answer_id})
    
    async def enqueue_originality_check(self, answer_id: str):
        """Enqueue answer for originality check"""
        await self._enqueue_task("originality_check", {"answer_id": answer_id})
    
    async def enqueue_expert_review(self, question_id: str, expert_id: str = None):
        """Enqueue question for expert review"""
        await self._enqueue_task("expert_review", {
            "question_id": question_id,
            "expert_id": expert_id
        })
    
    async def enqueue_delivery(self, question_id: str):
        """Enqueue answer for delivery"""
        await self._enqueue_task("delivery", {"question_id": question_id})
    
    async def enqueue_notification(self, user_id: str, message: str, notification_type: str = "info"):
        """Enqueue notification for user"""
        await self._enqueue_task("notification", {
            "user_id": user_id,
            "message": message,
            "type": notification_type
        })
    
    async def _enqueue_task(self, queue_name: str, data: Dict[str, Any]):
        """Generic method to enqueue tasks"""
        try:
            if not self.connection or self.connection.is_closed:
                await self.connect()
            
            message = json.dumps(data)
            self.channel.basic_publish(
                exchange="",
                routing_key=queue_name,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                )
            )
            
            logger.info(f"Task enqueued to {queue_name}: {data}")
            
        except Exception as e:
            logger.error(f"Failed to enqueue task to {queue_name}: {e}")
            raise
    
    async def consume_ai_processing(self, callback):
        """Consume AI processing tasks"""
        await self._consume_queue("ai_processing", callback)
    
    async def consume_humanization(self, callback):
        """Consume humanization tasks"""
        await self._consume_queue("humanization", callback)
    
    async def consume_originality_check(self, callback):
        """Consume originality check tasks"""
        await self._consume_queue("originality_check", callback)
    
    async def consume_expert_review(self, callback):
        """Consume expert review tasks"""
        await self._consume_queue("expert_review", callback)
    
    async def consume_delivery(self, callback):
        """Consume delivery tasks"""
        await self._consume_queue("delivery", callback)
    
    async def consume_notification(self, callback):
        """Consume notification tasks"""
        await self._consume_queue("notification", callback)
    
    async def _consume_queue(self, queue_name: str, callback):
        """Generic method to consume from queues"""
        try:
            if not self.connection or self.connection.is_closed:
                await self.connect()
            
            def on_message(channel, method, properties, body):
                try:
                    data = json.loads(body)
                    asyncio.create_task(callback(data))
                    channel.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    logger.error(f"Error processing message from {queue_name}: {e}")
                    channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=on_message
            )
            
            logger.info(f"Started consuming from {queue_name}")
            self.channel.start_consuming()
            
        except Exception as e:
            logger.error(f"Failed to consume from {queue_name}: {e}")
            raise
    
    def close(self):
        """Close RabbitMQ connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("RabbitMQ connection closed")
