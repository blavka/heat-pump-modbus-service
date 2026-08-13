FROM python:3.13-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY heat_pump_modbus_service ./heat_pump_modbus_service
RUN pip install --no-cache-dir . && \
    useradd --system --uid 10003 --create-home service
USER 10003:10003
ENTRYPOINT ["heat-pump-modbus-service"]
