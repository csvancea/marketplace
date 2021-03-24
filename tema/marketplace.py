"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import threading
from threading import Lock


class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """
    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """

        self._queue_size_per_producer = queue_size_per_producer

        self._producers = {}
        self._producers_cnt = 0
        self._register_lock = Lock()

        self._carts = {}
        self._carts_cnt = 0
        self._new_cart_lock = Lock()

        self._store = []
        self._product_to_producer = {}

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """

        with self._register_lock:
            producer_id = self._producers_cnt
            self._producers_cnt += 1

        self._producers[producer_id] = {}
        self._producers[producer_id]['count'] = 0
        self._producers[producer_id]['lock'] = Lock()

        return producer_id

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: Int
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """

        with self._producers[producer_id]['lock']:
            if self._producers[producer_id]['count'] == self._queue_size_per_producer:
                return False

            self._producers[producer_id]['count'] += 1

        self._product_to_producer[product] = producer_id
        self._store.append(product)

        return True

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """

        with self._new_cart_lock:
            cart_id = self._carts_cnt
            self._carts_cnt += 1

        self._carts[cart_id] = {}
        self._carts[cart_id]['store'] = []
        return cart_id

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """

        # Element removal is an atomic operation apparently, so no lock is required here
        # https://blog.finxter.com/python-list-remove/

        try:
            self._store.remove(product)
        except ValueError:
            # Product not found in store
            return False

        producer_id = self._product_to_producer[product]
        with self._producers[producer_id]['lock']:
            self._producers[producer_id]['count'] -= 1

        self._carts[cart_id]['store'].append(product)

        return True

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """

        producer_id = self._product_to_producer[product]
        with self._producers[producer_id]['lock']:
            if self._producers[producer_id]['count'] == self._queue_size_per_producer:
                return False

            self._producers[producer_id]['count'] += 1

        self._carts[cart_id]['store'].remove(product)
        self._store.append(product)

        return True

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """

        for product in self._carts[cart_id]['store']:
            print('{} bought {}'.format(threading.current_thread().name, product))
