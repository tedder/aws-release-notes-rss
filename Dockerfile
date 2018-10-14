FROM python:3.6-alpine

RUN apk add vim curl bash
COPY requirements.txt /opt/app/
RUN pip3 install --no-cache-dir -r /opt/app/requirements.txt
COPY aws-credentials /root/.aws/credentials
COPY scrape.py /opt/app/
CMD /opt/app/scrape.py

