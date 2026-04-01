FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir ".[anthropic,openai]"

COPY src/ src/

EXPOSE 8000

CMD ["uvicorn", "care.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
