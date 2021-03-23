"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import time
from threading import Thread


class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """

        Thread.__init__(self, **kwargs)

        self._carts = carts
        self._marketplace = marketplace
        self._retry_wait_time = retry_wait_time

    def run(self):
        for cart in self._carts:
            cart_id = self._marketplace.new_cart()

            for event in cart:
                fn = self._marketplace.add_to_cart if event['type'] == "add" \
                    else self._marketplace.remove_from_cart

                for _ in range(event['quantity']):
                    while not fn(cart_id, event['product']):
                        time.sleep(self._retry_wait_time)

            self._marketplace.place_order(cart)
