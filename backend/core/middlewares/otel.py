import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.logging import LoggingInstrumentor


def setup_otel() -> None:
    """
    OpenTelemetry TracerProvider 초기화.
    - 로그에 otelTraceID / otelSpanID 자동 주입
    - OTLP exporter 연동 전까지는 ConsoleSpanExporter 사용
    """
    service_name = os.getenv("OTEL_SERVICE_NAME", "shopping-backend")

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)

    # 개발용: 콘솔 exporter (OTLP 연동 시 이 부분을 OTLPSpanExporter로 교체)
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)

    # logging.LogRecord에 otelTraceID, otelSpanID, otelServiceName 필드 주입
    LoggingInstrumentor().instrument(set_logging_format=False)
