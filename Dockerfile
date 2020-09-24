FROM python:3.7-alpine
RUN apk add --update --no-cache g++ gcc libxslt-dev
COPY . /app
WORKDIR /app
RUN apk add build-base libxml2-dev libxslt-dev
RUN python setup.py install
CMD ["twitterscraper"]
