FROM python:3.12 AS builder

WORKDIR /build

COPY requirements.txt .
RUN python -m venv /opt/venv \
	&& /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim

RUN useradd --create-home --shell /usr/sbin/nologin noa

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY --chown=noa:noa app.py .

USER noa

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]