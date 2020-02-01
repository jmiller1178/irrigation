# -*- coding: utf-8 -*-

import pika
import logging
from django.conf import settings
from pika.spec import PERSISTENT_DELIVERY_MODE

logger = logging.getLogger(__name__)

class RabbitMqApi(object):

    def __init__(self, host, username, password):
        logger.debug("RabbitMqApi() establishing connection and channel")
        # Use plain credentials for authentication
        rabbitmq_credentials = pika.PlainCredentials(
            username=username,
            password=password)

        # Use localhost
        rabbitmq_params = pika.ConnectionParameters(
            host=host,
            credentials=rabbitmq_credentials,
            virtual_host="/")

        self.connection = pika.BlockingConnection(rabbitmq_params)
        self.channel = self.connection.channel()

    def __del__(self):
        logger.debug("RabbitMqApi() closing connection and channel")
        rabbit_warning = 'RabbitMqApi destructor called before {} was initialized.'
        rabbit_warning += '  This sometimes means RABBITMQ_HOST ({}) could not be resolved.'

        if hasattr(self, 'channel'):
            self.channel.close()
        else:
            message = rabbit_warning.format('channel', settings.RABBITMQ_HOST)
            logger.warning(message)
            print(message)

        if hasattr(self, 'connection'):
            self.connection.close()
        else:
            message = rabbit_warning.format('connection', settings.RABBITMQ_HOST)
            logger.warning(message)
            print(message)

    def enqueue_routed_order_message(self, queue, exchange, routing_key, order_message):
        success = False
        logger.debug("RabbitMqApi.enqueue_routed_order_message: {0} {1} {2} {3}".\
        format(exchange, queue, routing_key, order_message))

        # declare the exchange - we have one queue and one exchange but we vary the routing key
        # to process orders differently
        self.channel.exchange_declare(exchange=exchange,
                                      exchange_type=settings.ORDER_EXCHANGE_TYPE,
                                      durable=True)

        # declare the queue - we use durable flag to persist the queue to disk to avoid message loss
        self.channel.queue_declare(queue=queue, durable=True)

        # bind the queue and the exchange and set the routing key so we only publish messages to certain subscribers
        self.channel.queue_bind(queue=queue,
                           exchange=exchange,
                           routing_key=routing_key)

        # persistent means it won't go away if the rabbitmqctl service is restarted or server rebooted
        properties = pika.BasicProperties(delivery_mode=PERSISTENT_DELIVERY_MODE, )

        success = self.channel.basic_publish(exchange=exchange,
                                             routing_key=routing_key,
                                             body=order_message,
                                             properties = properties)

        return success


    def dequeue_routed_order_message(self, queue, exchange, routing_key):
        # declare the exchange - we have one queue and one exchange but we vary the routing key
        # to process orders differently
        self.channel.exchange_declare(exchange=exchange,
                                      exchange_type=settings.ORDER_EXCHANGE_TYPE,
                                      durable=True)

        # declare the queue - we use durable flag to persist the queue to disk to avoid message loss
        self.channel.queue_declare(queue=queue, durable=True)

        # bind the queue and the exchange and set the routing key so we only receive certain order messages
        self.channel.queue_bind(queue=queue,
                           exchange=exchange,
                           routing_key=routing_key)

        # invoke the basic_get which just reads a queued message
        method, properties, body = self.channel.basic_get(queue=queue)

        logger.debug("RabbitMqApi.dequeue_routed_order_message: {0} {1} {2} {3}".\
        format(exchange, queue, routing_key, body))

        # pass back the method and the body
        # the consumer, of this method, needs the method to pass into the acknowledge_message method below
        # the consumer is mostly interested in the body though
        return method, body


    def acknowledge_message(self, method):
        # acknowledges a particular message which removes it from the queue
        self.channel.basic_ack(delivery_tag=method.delivery_tag)

    def publish(self, **kwargs):
        exchange = kwargs.get('exchange', settings.DEFAULT_AMQ_TOPIC)
        routing_key = kwargs.get('routing_key', '')
        body = kwargs.get('body', '')

        self.channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=body)
