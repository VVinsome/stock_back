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
ENV PORT=8888
ENV DEBUG 0
ENV token pk_52ae86a3ff14418d86666498498aa228
ENV SECRET_KEY 'hz^9#5l0p@#n3n8gc5t36@uon9+x3jnan=q==8xl&4n=*((y#k'
ENV URL https://cloud.iexapis.com/stable/

# Install system dependencies
# RUN apt-get update && apt-get install -y --no-install-recommends \
#         tzdata \
#         python3-setuptools \
#         python3-pip \
#         python3-dev \
#         python3-venv \
#         git \
#         && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*


# install environment dependencies
RUN pip3 install pipenv

# Install project dependencies
RUN pipenv install --skip-lock --system --dev

# EXPOSE 8888
CMD gunicorn stockAPI.wsgi:application --bind 0.0.0.0:$PORT