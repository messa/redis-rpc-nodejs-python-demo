docker-build:
	docker build -t redisrpcdemo .

docker-run:
	docker run --rm -it -p 3000:3000 redisrpcdemo

run-redis:
	redis-server redis.conf
