#!/usr/bin/env python3
from opentelemetry.semconv.trace import HttpFlavorValues, SpanAttributes
from opentelemetry import trace
import requests
from common import configure_tracer, configure_meter
from opentelemetry.propagate import inject
import time
from common import start_recording_memory_metrics


tracer = configure_tracer("shopper", "0.1.2")
meter = configure_meter("shopper", "0.1.2")
total_duration_histo = meter.create_histogram(
    name="duration",
    description="request duration",
    unit="ms",
)
upstream_duration_histo = meter.create_histogram(
    name="upstream_request_duration",
    description="duration of upstream requests",
    unit="ms",
)


@tracer.start_as_current_span("browse")
def browse():
    print("visiting the grocery store")
    with tracer.start_as_current_span(
        "web request", kind=trace.SpanKind.CLIENT, record_exception=False, set_status_on_exception=True
    ) as span:
        start = time.time_ns()
        url = "http://localhost:5000/products"
        headers = {}
        inject(headers)
        span = trace.get_current_span()
        span.set_attributes(
            {
                SpanAttributes.HTTP_METHOD: "GET",
                SpanAttributes.HTTP_FLAVOR: HttpFlavorValues.HTTP_1_1.value,
                SpanAttributes.HTTP_URL: "http://localhost:5000",
                SpanAttributes.NET_PEER_IP: "127.0.0.1",
            }
        )
        span.add_event("about to send a request")
        resp = requests.get(url, headers=headers)
        # resp = requests.get("invalid_url", headers=headers)
        span.add_event("request sent", attributes={"url": url}, timestamp=0)
        span.set_attribute(SpanAttributes.HTTP_STATUS_CODE, resp.status_code)
        duration = (time.time_ns() - start)/1e6
        upstream_duration_histo.record(duration)
    # add_item_to_cart("orange", 5)


# @tracer.start_as_current_span("add item to cart")
# def add_item_to_cart(item, quantity):
#     span = trace.get_current_span()
#     span.set_attributes(
#         {
#             "item": item,
#             "quantity": quantity,
#         }
#     )
#     print("add {} to cart".format(item))


@tracer.start_as_current_span("visit store")
def visit_store():
    start = time.time_ns()
    browse()
    duration = (time.time_ns() - start)/1e6
    total_duration_histo.record(duration)


if __name__ == "__main__":
    start_recording_memory_metrics(meter)
    visit_store()
    print("finished")
