#!/usr/bin/env python3

import argparse
from datetime import timedelta
import logging
from time import time
from time import monotonic as monotime
from uuid import uuid4
import simplejson as json
import sys
from reprlib import repr as smart_repr

import redis


logger = logging.getLogger(__name__)


class RedisRPCClient:

    def __init__(self, redis_client, service_name):
        self._redis = redis_client
        self._service_name = service_name

    def call(self, method_name, params):
        assert isinstance(params, dict)
        req_key = 'rpc-req:{service}'.format(service=self._service_name)
        req_timeout = timedelta(seconds=30)
        token = uuid4().hex
        req_payload = {
            'method': method_name,
            'params': params,
            'token': token,
            'expire': time() + req_timeout.total_seconds(),
        }
        logger.info('Calling %s(%s)', method_name, smart_repr(params))
        self._redis.expire(req_key, req_timeout)
        self._redis.rpush(req_key, json.dumps(req_payload, sort_keys=True).encode())

        res_key = 'rpc-res:{service}:{token}'.format(service=self._service_name, token=token)
        res = self._redis.blpop(res_key, int(req_timeout.total_seconds()) or 1)
        if not res:
            raise Exception('RPC call timeout')
        res_key, res_data = res
        res_payload = json.loads(res_data.decode())
        if res_payload.get('error'):
            raise Exception('RPC handler failed: {}'.format(res_payload['error']))
        return res_payload['reply']


def main():
    p = argparse.ArgumentParser()
    p.add_argument('service')
    p.add_argument('method')
    p.add_argument('params', nargs='?')
    args = p.parse_args()

    params = json.loads(args.params) if args.params else {}

    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    print(r)

    client = RedisRPCClient(r, args.service)
    try:
        print(client.call(args.method, params))
    except Exception as e:
        sys.exit('ERROR: ' + repr(e))


if __name__ == '__main__':
    main()
