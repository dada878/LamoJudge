FROM alpine
RUN apk add --no-cache build-base g++
WORKDIR /code
COPY . /code
CMD ["/bin/sh"]