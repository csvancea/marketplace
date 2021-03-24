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

        # Producers are stored here
        # Lock needed to increment/decrement producers count atomically
        self._producers = {}
        self._producers_cnt = 0
        self._register_lock = Lock()

        # Carts are stored here
        # Lock needed to increment/decrement carts count atomically
        self._carts = {}
        self._carts_cnt = 0
        self._new_cart_lock = Lock()

        # All published products are stored here
        self._store = []

        # Map a product to its producer
        # (needed because products from all producers are stored in a the same list)
        self._product_to_producer = {}

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """

        with self._register_lock:
            producer_id = self._producers_cnt
            self._producers_cnt += 1

        # previous lock assures me that producer_id is an unique value
        # (2 parallel register_producer calls can't return the same id)

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

        # Make sure the producer queue isn't full
        # While only 1 thread can publish products, multiple threads (consumers)
        # can consume products, so a lock is needed
        with self._producers[producer_id]['lock']:
            if self._producers[producer_id]['count'] == self._queue_size_per_producer:
                return False

            # Increment the product count for producer_id
            self._producers[producer_id]['count'] += 1

        # No sync needed
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

        # previous lock assures me that cart_id is an unique value
        # (2 parallel new_cart calls can't return the same id)

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

        # Atomically decrease the product count of producer

        producer_id = self._product_to_producer[product]
        with self._producers[producer_id]['lock']:
            self._producers[producer_id]['count'] -= 1

        # Carts are not shared between threads (consumers)
        # No race conditions here

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

        # Attempt to increase the product count of producer
        # If queue is full (can't increase), inform the consumer to try again (return False)

        producer_id = self._product_to_producer[product]
        with self._producers[producer_id]['lock']:
            if self._producers[producer_id]['count'] == self._queue_size_per_producer:
                return False

            self._producers[producer_id]['count'] += 1

        # Carts are not shared between threads (consumers)
        # no race conditions here

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
