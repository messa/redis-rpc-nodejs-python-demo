FROM node:8-stretch

MAINTAINER Petr Messner

ENV PYTHONUNBUFFERED=1 NODE_ENV=production

RUN apt-get update
RUN apt-get install -y python3-redis python3-simplejson redis-server

COPY web/package.json web/yarn.lock /app/web/
RUN cd /app/web && yarn install

COPY runner.py redis.conf /app/
COPY backend/ /app/backend/
COPY web/ /app/web/

RUN cd /app/web && yarn build

WORKDIR /app

EXPOSE 3000

CMD ["./runner.py"]
