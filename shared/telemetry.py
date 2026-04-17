import asyncio
import logging
import os
from functools import wraps

from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter


def _is_enabled() -> bool:
    return os.getenv("TELEMETRY_ENABLED", "true").lower() == "true"


def init_telemetry() -> None:
    """
    Initialize OpenTelemetry tracing and logging.

    Set TELEMETRY_ENABLED=false to disable (e.g. during tests or local dev
    without a running collector).

    Reads configuration from standard OTel environment variables:
      OTEL_SERVICE_NAME           — name of the service (e.g. "ingestion-service")
      OTEL_EXPORTER_OTLP_ENDPOINT — OTLP collector endpoint (e.g. "http://otel-collector:4317")

    Call once at application startup (e.g. in main.py).
    """
    if not _is_enabled():
        return
    _init_tracing()
    _init_logging()


def _init_tracing() -> None:
    provider = TracerProvider()
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)


def _init_logging() -> None:
    logger_provider = LoggerProvider()
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(OTLPLogExporter())
    )
    set_logger_provider(logger_provider)
    logging.getLogger().addHandler(LoggingHandler())
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.getLogger().setLevel(logging.INFO)


def traced(span_name: str = None, attributes: dict = None):
    """
    Decorator that wraps a function in an OpenTelemetry span.

    Supports both sync and async functions. Example usage:

        @traced("ingest_pipeline.run")
        def run(self, text, name, metadata): ...

        @traced("query_pipeline.embed", attributes={"model": "text-embedding-3-small"})
        def _embed(self, state): ...
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracer = trace.get_tracer(func.__module__)
            with tracer.start_as_current_span(span_name or func.__name__) as span:
                if attributes:
                    for k, v in attributes.items():
                        span.set_attribute(k, v)
                return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            tracer = trace.get_tracer(func.__module__)
            with tracer.start_as_current_span(span_name or func.__name__) as span:
                if attributes:
                    for k, v in attributes.items():
                        span.set_attribute(k, v)
                return func(*args, **kwargs)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator
