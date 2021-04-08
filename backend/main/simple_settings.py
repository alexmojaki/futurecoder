import sys

import sentry_sdk
import snoop
from dryenv import DryEnv, populate_globals
from littleutils import setup_quick_console_logging
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.executing import ExecutingIntegration
from sentry_sdk.integrations.pure_eval import PureEvalIntegration

setup_quick_console_logging()


class Root(DryEnv):
    DEBUG = True

    SEPARATE_WORKER_PROCESS = False
    MASTER_URL = "http://localhost:5000/"
    SET_LIMITS = True

    SAVE_CODE_ENTRIES = True

    SENTRY_DSN = ""
    SECRET_KEY = 'kt1+4_u=ga%3v3@fy0@7c(&lq%)6tt=c+f-(ihd32@t$)i6gjm'
    GITHUB_TOKEN = ""

    DISABLE_HTTPS = False


class MONITOR(DryEnv):
    PROCESS_HISTORY_SIZE = 3
    ACTIVE = False
    SLEEP_TIME = 15
    MAX_SINCE = 60 * 60


class GITHUB_APP(DryEnv):
    ID = ''
    SECRET = ''


class FACEBOOK_APP(DryEnv):
    ID = ''
    SECRET = ''


class GOOGLE_APP(DryEnv):
    ID = ''
    SECRET = ''


snoop.install(enabled=Root.DEBUG, out=sys.__stderr__, columns=['thread'])

sentry_sdk.init(
    dsn=Root.SENTRY_DSN,
    integrations=[DjangoIntegration(), PureEvalIntegration(), ExecutingIntegration()],
    send_default_pii=True
)

populate_globals()
