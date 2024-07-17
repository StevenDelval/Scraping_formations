FROM mcr.microsoft.com/azure-functions/python:4-python3.11

ENV host:logger:consoleLoggingMode=always

COPY . /home/site/wwwroot

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    playwright install-deps && \
    playwright install