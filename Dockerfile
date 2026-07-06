# ===== Builder stage =====
FROM python:3.11-alpine AS builder

WORKDIR /app

RUN apk add --no-cache build-base

COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

# ===== Runtime stage =====
FROM python:3.11-alpine

WORKDIR /app

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy app source
COPY . .

ENV PYTHONUNBUFFERED=1
ENV PORT=8000

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8000/ || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
