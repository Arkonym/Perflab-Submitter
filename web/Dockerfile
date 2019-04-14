FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir -p perfserv/code/
RUN mkdir perfserv/uploads
WORKDIR perfserv/code
ADD requirements.txt ./
RUN pip install -r requirements.txt
