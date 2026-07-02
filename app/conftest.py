import sys
from unittest.mock import MagicMock

# 1. Intercept the redis module globally before pytest imports any app files
mock_redis_module = MagicMock()
sys.modules['redis'] = mock_redis_module

# 2. Configure default mock connection behaviors so your app thinks it is talking to a healthy database
mock_client = MagicMock()
mock_redis_module.Redis.return_value = mock_client

# Simulate successful ping and basic cache hits/writes
mock_client.ping.return_value = True
mock_client.get.return_value = None
mock_client.set.return_value = True
