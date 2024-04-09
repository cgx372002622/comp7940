# Use the Python image
FROM python:3.9.19-slim-bullseye


# Set working directory in the container
WORKDIR /APP


# Copy the Python scripts and other files to the container
COPY . /APP


# Install dependencies
RUN pip install update
RUN pip install -r requirements.txt


# Set environment variables
ENV CHATGPT_ACCESS_TOKEN=39f1ce87-0487-4361-a4ea-78c88c216a4b
ENV CHATGPT_BASICURL=https://chatgpt.hkbu.edu.hk/general/rest
ENV CHATGPT_MODELNAME=gpt-35-turbo
ENV REDIS_HOST=redis-18082.c295.ap-southeast-1-1.ec2.cloud.redislabs.com
ENV REDIS_PASSWORD=PNRh1AkwURh8novG2j7Vv4g6mj4JCHlZ
ENV REDIS_REDISPORT=18082
ENV TELEGRAM_ACCESS_TOKEN=6065911282:AAGGO0FXc_dhrXbGVJA-sNme2GBCvZ3xldo


# Set the entrypoint
CMD python chatbot.py