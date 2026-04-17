import os

# Disable telemetry during tests to avoid connection errors
# when no OTel collector is running.
os.environ.setdefault("TELEMETRY_ENABLED", "false")
