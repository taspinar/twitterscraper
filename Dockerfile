FROM python:3.7-alpine
COPY . /app
WORKDIR /app

RUN apk add --no-cache \
    gcc \
    libc-dev \
    libxml2-dev \
    libxslt-dev
RUN python setup.py install

CMD ["twitterscraper"]
