FROM python:3.6-alpine
MAINTAINER Josha Inglis <josha.inglis@biarri.com>

COPY src/requirements.txt /reqs/requirements.txt
RUN apk --no-cache add tini && pip install -r /reqs/requirements.txt

COPY src/ /usr/src/app
WORKDIR /usr/src/app

RUN pip install -e .

ENTRYPOINT ["/sbin/tini", "--", "qikfiller"]
