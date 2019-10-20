FROM python:3.7-alpine
COPY . /app
WORKDIR /app
RUN python setup.py install
CMD ["twitterscraper"]
