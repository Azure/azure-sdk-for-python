import subprocess
import functools
import sys
import os
import pytest
import pprint

def run(cmd, my_env):
    os.environ['PYTHONUNBUFFERED'] = "1"
    proc = subprocess.Popen(cmd,
        stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT,
        env = my_env
    )
    stdout, stderr = proc.communicate()

    return proc.returncode, stdout, stderr

def _test_file(file_name, folder):
    path_to_sample = os.path.abspath(
        os.path.join(os.path.abspath(__file__), "..", "..", "./samples/" + folder + "/" + file_name))
    my_env = dict(os.environ)
    if sys.version_info < (3, 5):
        my_env = {key: str(val) for key, val in my_env.items()}
    code, out, err = run([sys.executable, path_to_sample], my_env=my_env)
    try:
        assert code == 0
        assert err is None
    except AssertionError as e:
        e.args += (out, )
        raise AssertionError(e)

class TestSamples():

    def test_champion_scenarios(self):
        _test_file('cs1_publish_custom_events_to_a_topic.py', 'champion_scenarios')
        _test_file('cs1b_publish_custom_events_to_a_topic_with_signature.py', 'champion_scenarios')
        #_test_file('cs2_publish_custom_events_to_a_domain_topic.py', 'champion_scenarios')
        _test_file('cs3_consume_system_events.py', 'champion_scenarios')
        _test_file('cs4_consume_custom_events.py', 'champion_scenarios')
        _test_file('cs5_publish_events_using_cloud_events_1.0_schema.py', 'champion_scenarios')
        _test_file('cs6_consume_events_using_cloud_events_1.0_schema.py', 'champion_scenarios')
    
    def test_publish_samples(self):
        _test_file('publish_cloud_events_to_custom_topic_sample.py', 'publish_samples')
        _test_file('publish_cloud_events_to_domain_topic_sample.py', 'publish_samples')
        _test_file('publish_custom_schema_events_to_topic_sample.py', 'publish_samples')
        _test_file('publish_event_grid_events_to_custom_topic_sample.py', 'publish_samples')
        _test_file('publish_with_shared_access_signature_sample.py', 'publish_samples')
    
    def test_consume_samples(self):
        _test_file('consume_cloud_custom_data_sample.py', 'consume_samples')
        _test_file('consume_eg_storage_blob_created_data_sample.py', 'consume_samples')