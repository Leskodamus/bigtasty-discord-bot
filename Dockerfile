FROM python:3.10
RUN pip install requests py-cord openai
WORKDIR /usr/app/src

