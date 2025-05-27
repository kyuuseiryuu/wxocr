FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install flask flask_cors

COPY wcocr.cpython-312-x86_64-linux-gnu.so /app/wcocr.cpython-312-x86_64-linux-gnu.so

COPY wx /app/wx

COPY main.py /app/main.py

WORKDIR /app

EXPOSE 5000

CMD ["python", "main.py"]