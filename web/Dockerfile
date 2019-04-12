FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
RUN mkdir /code/uploads
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
