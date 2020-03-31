import os

import sentry_sdk
from littleutils import setup_quick_console_logging
from sentry_sdk.integrations.django import DjangoIntegration

setup_quick_console_logging()

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    integrations=[DjangoIntegration()],
    send_default_pii=True
)

SEPARATE_WORKER_PROCESS = os.environ.get('SEPARATE_WORKER_PROCESS', 'False')[0].upper() == 'T'

MASTER_URL = os.environ.get('MASTER_URL', "http://localhost:5000/")
