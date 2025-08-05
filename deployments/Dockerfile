# Separate build image
FROM python:3.12-slim AS builder
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Final image
FROM python:3.12-slim
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3/site-packages
ENV PYTHONPATH=/usr/local/lib/python3/site-packages

WORKDIR /src
COPY . /src/

EXPOSE 8000

CMD ["python", "-m", "app"]