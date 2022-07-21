from dateutil import tz
from typing import Dict, Union

from azure.ai.ml.entities import CronSchedule, RecurrenceSchedule, RecurrencePattern


def _check_recurrence_schedule_fields(job_schedule: RecurrenceSchedule, job_dict_schedule: Dict):
    assert isinstance(job_schedule, RecurrenceSchedule)
    _check_common_schedule_fields(job_schedule, job_dict_schedule)
    print(job_schedule.frequency)
    print(job_dict_schedule["frequency"])
    assert job_schedule.frequency == job_dict_schedule["frequency"]
    assert job_schedule.interval == job_dict_schedule["interval"]

    job_schedule_pattern = job_schedule.pattern
    job_dict_schedule_pattern = job_dict_schedule.get("pattern", None)
    if job_dict_schedule_pattern:
        assert job_schedule_pattern
        assert isinstance(job_schedule_pattern, RecurrencePattern)

        # Since literal values are allowed in YAML, convert non-list values to lists
        # to check that the SDK is internally storing "hours", "minutes", and "weekdays" as lists.
        job_dict_schedule_pattern_hours = job_dict_schedule_pattern["hours"]
        if not isinstance(job_dict_schedule_pattern_hours, list):
            job_dict_schedule_pattern_hours = [job_dict_schedule_pattern_hours]
        job_dict_schedule_pattern_minutes = job_dict_schedule_pattern["minutes"]
        if not isinstance(job_dict_schedule_pattern_minutes, list):
            job_dict_schedule_pattern_minutes = [job_dict_schedule_pattern_minutes]
        job_dict_scheudule_pattern_weekdays = job_dict_schedule_pattern["weekdays"]
        if not isinstance(job_dict_scheudule_pattern_weekdays, list):
            job_dict_scheudule_pattern_weekdays = [job_dict_scheudule_pattern_weekdays]

        # SDK behavior is to store the hours/minutes/weekdays as a list but also allow the user to set single, literal values for each of them
        assert isinstance(job_schedule_pattern.hours, list)
        assert job_schedule_pattern.hours == job_dict_schedule_pattern_hours
        assert isinstance(job_schedule_pattern.minutes, list)
        assert job_schedule_pattern.minutes == job_dict_schedule_pattern_minutes
        assert isinstance(job_schedule_pattern.weekdays, list)
        assert [day.lower() for day in job_schedule_pattern.weekdays] == job_dict_scheudule_pattern_weekdays


def _check_common_schedule_fields(job_schedule: Union[CronSchedule, RecurrenceSchedule], job_dict_schedule: Dict):
    # normalize timezone to UTC to prevent issues arising from differing timezone representations.
    assert job_schedule.start_time
    assert job_schedule.time_zone == job_dict_schedule.get("time_zone", "UTC")
    assert job_schedule.status == job_dict_schedule["status"]


_PIPELINE_JOB_TIMEOUT_SECOND = 20 * 60  # timeout for pipeline job's tests, unit in second.
