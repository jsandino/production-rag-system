import asyncio

import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from shared.telemetry import _is_enabled, traced


# --- _is_enabled ---

def test_is_enabled_when_set_to_true(monkeypatch):
    monkeypatch.setenv("TELEMETRY_ENABLED", "true")
    assert _is_enabled() is True


def test_is_disabled_when_set_to_false(monkeypatch):
    monkeypatch.setenv("TELEMETRY_ENABLED", "false")
    assert _is_enabled() is False


def test_is_enabled_by_default(monkeypatch):
    monkeypatch.delenv("TELEMETRY_ENABLED", raising=False)
    assert _is_enabled() is True


def test_is_disabled_case_insensitive(monkeypatch):
    monkeypatch.setenv("TELEMETRY_ENABLED", "False")
    assert _is_enabled() is False


# --- traced decorator ---

@pytest.fixture(scope="session", autouse=True)
def setup_tracer_provider():
    """Register an in-memory TracerProvider once for the entire test session.
    OTel only allows set_tracer_provider() to be called once per process."""
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    return exporter


@pytest.fixture
def span_exporter(setup_tracer_provider):
    """Yield a clean exporter for each test by clearing spans before use."""
    setup_tracer_provider.clear()
    yield setup_tracer_provider


def test_traced_sync_function_returns_value():
    @traced("test.sync")
    def add(a, b):
        return a + b

    assert add(1, 2) == 3


def test_traced_sync_creates_span(span_exporter):
    @traced("test.sync_span")
    def greet():
        return "hello"

    greet()

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    assert spans[0].name == "test.sync_span"


def test_traced_defaults_to_function_name(span_exporter):
    @traced()
    def my_function():
        pass

    my_function()

    spans = span_exporter.get_finished_spans()
    assert spans[0].name == "my_function"


def test_traced_sets_attributes(span_exporter):
    @traced("test.attributes", attributes={"model": "gpt-4o", "version": "1"})
    def call_llm():
        pass

    call_llm()

    span = span_exporter.get_finished_spans()[0]
    assert span.attributes["model"] == "gpt-4o"
    assert span.attributes["version"] == "1"


def test_traced_async_function_returns_value():
    @traced("test.async")
    async def fetch():
        return "result"

    assert asyncio.run(fetch()) == "result"


def test_traced_async_creates_span(span_exporter):
    @traced("test.async_span")
    async def fetch():
        return "result"

    asyncio.run(fetch())

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1
    assert spans[0].name == "test.async_span"


def test_traced_wraps_sync_not_async():
    def sync_fn():
        pass

    wrapped = traced()(sync_fn)
    assert not asyncio.iscoroutinefunction(wrapped)


def test_traced_wraps_async_not_sync():
    async def async_fn():
        pass

    wrapped = traced()(async_fn)
    assert asyncio.iscoroutinefunction(wrapped)
