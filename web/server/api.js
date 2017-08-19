import { Router } from 'express'
import Redis from 'ioredis'

const router = Router();
export default router;

const createRedis = () => {
  console.info('createRedis');
  return new Redis();
}
const redisPool = [];

const getRedis = async (f) => {
  const redis = redisPool.pop() || createRedis();
  const res = await f(redis);
  redisPool.push(redis);
  return res;
};

router.post('/performCall', (req, res) => {
  getRedis(async (redis) => {
    console.info('performCall:', req.body);
    const { serviceName, methodName, params } = req.body;
    const token = 'node' + process.pid + '_' + new Date() * 1;
    const reqKey = `rpc-req:${serviceName}`;
    const resKey = `rpc-res:${serviceName}:${token}`;
    const timeoutSeconds = 10;
    const reqPayload = {
      token, params,
      method: methodName,
      expire: (new Date() / 1000) + timeoutSeconds,
    };
    // console.info(reqKey, reqPayload);
    redis.rpush(reqKey, JSON.stringify(reqPayload));
    const result = await redis.blpop(resKey, timeoutSeconds);
    res.json(JSON.parse(result[1]));
  });
});
