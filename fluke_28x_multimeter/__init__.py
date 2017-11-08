# -*- coding: utf-8 -*-

"""Top-level package for Fluke 28x Multimeter."""

__author__ = """Moritz Federspiel"""
__email__ = 'moritz.federspiel@steadysense.at'
__version__ = '0.1.0'

from .query import *
import logging

logger = logging.getLogger(__name__)

class Fluke287(object):
    """
    Base object for communication with Fluke287 Multimeter
    """
    queries = {q.__name__: q for q in [QM, QDDA, ID]}

    def __init__(self, io=None, port=None):
        if io is None:
            if port is None:
                port = self.find_serial()
            self.connect(port)
        else:
            self._io = io
        self.name = self.__class__.__name__

    @staticmethod
    def find_serial():
        return find()

    def connect(self, port=None):
        self._io = connect(port)
        logger.info(f"Connected to {self._io}")

    def disconnect(self):
        ret = disconnect(self._io)
        logger.info("Disconnected from {self._io}")
        return ret

    def send(self, request):
        return send(self._io, request)

    def recv(self):
        return receive(self._io)

    @property
    def is_connected(self):
        """
        :return: True if connected else False
        """
        return self._io.is_open

    @classmethod
    def find_query(cls, query):
        """
        :param query: query name or class
        :return: query or ValueError
        """
        for name, q in cls.queries.items():
            if query is q:
                return query
            elif query == name:
                return q
        raise ValueError(f"Unknown Query {query}")

    def execute(self, query, *args, **kwargs):
        """
        execute a query, args and kwargs are passed to query
        :param query: query name or class
        :param args: query arguments
        :param kwargs: query keyword arguments
        :return: 
        """
        logger.info(f"Executing {query}({args}, {kwargs})")
        q = self.find_query(query)
        request = q.execute(self, *args, **kwargs)
        return request.response.data

    @property
    def status(self):
        return dict(
            name=self.__class__.__name__,
            device=self.id if self.is_connected else {},
            queries=list(self.queries.keys()),
            connection=settings(self._io),
            connected=self.is_connected
        )

    @property
    def id(self):
        """ return identification dict """
        return self.execute(ID)

    @property
    def values(self):
        """ returns all displayed data"""
        return self.execute(QDDA)

    @property
    def value(self):
        """ returns primary value, unit and mode """
        return self.execute(QM)
