from prometheus_client import Counter, Gauge

PAYMENTS_TOTAL = Counter(
    "payments_total",
    "Total payment outcomes",
    ["status"],
)

ACTIVE_SUBSCRIPTIONS = Gauge(
    "active_subscriptions",
    "Currently active subscriptions",
)
