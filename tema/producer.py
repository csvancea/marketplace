"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import time
from threading import Thread


class Producer(Thread):
    """
    Class that represents a producer.
    """

    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        """
        Constructor.

        @type products: List()
        @param products: a list of products that the producer will produce

        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace

        @type republish_wait_time: Time
        @param republish_wait_time: the number of seconds that a producer must
        wait until the marketplace becomes available

        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()
        """

        Thread.__init__(self, **kwargs)

        self._producer_id = marketplace.register_producer()

        self._products = products
        self._marketplace = marketplace
        self._republish_wait_time = republish_wait_time

    def run(self):
        while True:
            for product in self._products:
                product_type = product[0]
                product_qty = product[1]
                product_wait = product[2]

                for _ in range(product_qty):
                    while not self._marketplace.publish(self._producer_id, product_type):
                        time.sleep(self._republish_wait_time)

                    time.sleep(product_wait)
