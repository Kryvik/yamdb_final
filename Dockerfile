FROM python:3.7-slim

WORKDIR /app

COPY requirements.txt ./

RUN /bin/sh -c pip3 install -r /requirements.txt --no-cache-dir

RUN pip3 install -r requirements.txt --no-cache-dir

CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000" ] 
 