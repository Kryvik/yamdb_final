FROM python:3.7-slim

WORKDIR /app/api_yamdb

COPY requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000" ] 
 