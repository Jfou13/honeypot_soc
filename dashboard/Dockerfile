FROM python:3.9-slim
RUN pip install flask mysql-connector-python
WORKDIR /app
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
