# -*- coding: utf-8 -*-

import pytest
import time

from .server import InfinispanServer
from infinispan.client import Infinispan
from infinispan import exception


class TestClient(object):
    @classmethod
    def setup_class(cls):
        cls.server = InfinispanServer()
        cls.server.start()

    @classmethod
    def teardown_class(cls):
        try:
            cls.server.stop()
        except RuntimeError:
            # is ok, already stopped
            pass

    @pytest.yield_fixture
    def client(self):
        client = Infinispan()
        yield client
        client.disconnect()

    def test_put(self, client):
        result = client.put("key1", "value1")

        assert result is None

    def test_get(self, client):
        value = client.get("key1")

        assert value == "value1"

    def test_put_with_lifespan(self, client):
        result = client.put("key2", "value2", lifespan='2s')
        assert result is None

        value = client.get("key2")
        assert value == "value2"

        time.sleep(2)
        value = client.get("key2")
        assert value is None

    def test_put_with_max_idle(self, client):
        result = client.put("key3", "value3", max_idle='2s')
        assert result is None

        time.sleep(1)
        value = client.get("key3")
        assert value == "value3"

        time.sleep(1)
        value = client.get("key3")
        assert value == "value3"

        time.sleep(2)
        value = client.get("key3")
        assert value is None

    def test_remove(self, client):
        result = client.remove("key1")

        assert result is None

    def test_contains_key(self, client):
        assert client.contains_key("key1") is False
        client.put("key1", "value1")
        assert client.contains_key("key1") is True

    def test_get_non_existing(self, client):
        value = client.get("notexisting")

        assert value is None

    def test_put_to_different_cache(self, client):
        client.cache_name = "namedCache"
        result = client.put("key2", "value2")
        value2 = client.get("key2")
        value1 = client.get("key1")

        assert result is None
        assert value2 == "value2"
        assert value1 is None

    def test_put_to_non_existing_cache(self, client):
        client.cache_name = "nonexistingCache"
        with pytest.raises(exception.ClientError):
            client.put("key1", "value1")

    def test_context_manager(self):
        with Infinispan() as client:
            assert client.conn.connected is True
        assert client.conn.connected is False