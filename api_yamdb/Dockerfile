FROM python:3.7-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt

RUN cd api_yamdb

CMD ["gunicorn", "wsgi:application", "--bind", "0:8000" ] 
