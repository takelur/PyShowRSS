FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
COPY config .
COPY main.py .
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT ["python3", "main.py"]
