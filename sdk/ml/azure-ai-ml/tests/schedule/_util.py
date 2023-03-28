from datetime import datetime, timedelta

_SCHEDULE_TIMEOUT_SECOND = 20 * 60  # timeout for schedule's tests, unit in second.

TRIGGER_ENDTIME = (datetime(year=2099, month=1, day=1)).strftime("%Y-%m-%d %H:%M:%S")
TRIGGER_ENDTIME_DICT = [{"trigger.end_time": TRIGGER_ENDTIME}]  # trigger endtime can not be past time.
