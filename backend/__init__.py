# backend/__init__.py
import os
print(f"APP_ENV: {os.environ.get('APP_ENV')}")
# ... rest of your Redis initialization ...
"""# backend/__init__.py
import os
import redis

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))

r = None  # Initialize to None

if os.environ.get('APP_ENV') != 'testing':
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        r.ping()
        print("Connected to Redis")
    except redis.exceptions.ConnectionError as e:
        print(f"Could not connect to Redis: {e}")
    except redis.exceptions.TimeoutError as e:
        print(f"Timeout connecting to Redis: {e}")

# You might have other initializations here"""