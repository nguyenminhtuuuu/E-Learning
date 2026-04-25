from python:3.10-slim

workdir /app

copy requirements.txt .
run pip install --no-cache-dir -r requirements.txt

copy . /app/backend

expose 5000

cmd ["flask", "run", "--host=0.0.0.0"]