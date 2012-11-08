# Installation

You need Python, Redis and redis-py installed:

- [Python](http://www.python.org/)
- [Redis](http://redis.io)
- [redis-py](https://github.com/andymccurdy/redis-py)

# Checkout

Checkout this repo.

# Running

- Start a redis server on localhost
- Start a redis client
- Start a python runtime, start a service

		import service

		s = service.CounterService(1)
		s.subscribe(0)
		s.run()

- In redis client, do 

		PUBLISH service:0:channel 1

