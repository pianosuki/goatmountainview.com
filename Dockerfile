FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

RUN mkdir -p /app/app/static/images/uploads/soap \
    /app/app/static/images/uploads/does \
    /app/app/static/images/uploads/adoptions \
    /app/app/static/images/uploads/foundation \
    /app/instance

CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8000", "--pythonpath", "/app"]
