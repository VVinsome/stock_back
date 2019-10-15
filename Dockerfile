FROM python:3.7.4-slim-buster

# create and set working directory
RUN mkdir /app
WORKDIR /app

# Add current directory code to working directory
ADD . /app/

# set default environment variables
ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive 

# set project environment variables
# grab these via Python's os.environ
# these are 100% optional here


# install environment dependencies
RUN pip3 install pipenv

# Install project dependencies
RUN pipenv install --skip-lock --system --dev

# EXPOSE 8888
CMD gunicorn stockAPI.wsgi:application --bind 0.0.0.0:$PORT