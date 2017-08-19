#!/usr/bin/env python3

import argparse
import logging
from reprlib import repr as smart_repr
import simplejson as json
import sys
from time import time, sleep
from time import monotonic as monotime

import redis

from rpc_client import RedisRPCClient


logger = logging.getLogger(__name__)


def expose(f):
    f.exposed = True
    return f


class Handlers:

    def __init__(self, redis_client):
        self._rpc_client = RedisRPCClient(redis_client, 'echo')

    def get_routes(self):
        return {k: getattr(self, k) for k in dir(self) if not k.startswith('_') and getattr(getattr(self, k), 'exposed', False)}

    @expose
    def hello(self, params):
        return {'hello': 'Hello, World!'}

    @expose
    def sleep(self, params):
        sleep(params.get('seconds') or 5)
        return {'done': True}

    @expose
    def ping(self, params):
        return {'pong': params}

    @expose
    def fib(self, params):
        n = params.get('n', 10)
        if n <= 1:
            return {'f': 1}
        else:
            f = self._rpc_client.call('fib', {'n': n-1})['f']
            f += self._rpc_client.call('fib', {'n': n-2})['f']
            return {'f': f}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--one', '-1', action='store_true', help='process only one request')
    p.add_argument('--verbose', '-v', action='store_true')
    args = p.parse_args()

    logging.basicConfig(
        format='%(asctime)s %(name)s %(levelname)5s: %(message)s',
        level=logging.DEBUG if args.verbose else logging.WARNING)


    r = redis.StrictRedis(host='localhost', port=6379, db=0)

    handlers = Handlers(r)
    routes = handlers.get_routes()

    service_name = 'echo'
    req_key = 'rpc-req:{service}'.format(service=service_name)

    logger.debug('req_key: %r', req_key)

    while True:
        try:
            data = r.blpop(req_key, 10)
        except KeyboardInterrupt as e:
            # do not make too verbose traceback
            sys.exit('{!r} while redis blpop'.format(e))
        if data is None:
            continue
        key, value = data

        try:
            req_payload = json.loads(value.decode())
        except Exception as e:
            logger.error('Failed to parse request JSON: %r; value: %r', e, smart_repr(value))
            continue

        logger.debug('Request: %s', smart_repr(req_payload))

        now = time()
        if req_payload['expire'] < now:
            logger.info('Request expired %.3f s ago', now - req_payload['expire'])
            continue

        handler = routes.get(req_payload['method'])
        if handler is None:
            logger.warning('Method not found: %r', req_payload['method'])
            response = {'error': 'Method {!r} not found'.format(req_payload['method'])}
        else:
            try:
                reply = handler(req_payload['params'])
                response = {'reply': reply}
            except Exception as e:
                logger.exception('Method %r handler %r failed: %r', req_payload['method'], handler, e)
                response = {'error': repr(e)}

        res_key = 'rpc-res:{service}:{token}'.format(service=service_name, token=req_payload['token'])
        #logger.debug('res_key: %r', res_key)
        res_json = json.dumps(response, sort_keys=True).encode()
        r.rpush(res_key, res_json)
        r.expire(res_key, 60)

        if args.one:
            break


if __name__ == '__main__':
    main()
