from python import python_process
from go import go_process
from java import java_process
from js import js_process
from common import Common

import os
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(funcName)s[line:%(lineno)d] - %(levelname)s: %(message)s')
_LOG = logging.getLogger(__name__)

_LANGUAGES = {
    'python': python_process,
    'java': java_process,
    'go': go_process,
    'js': js_process
}


def main():
    language = os.getenv('LANGUAGE')
    languages = {language: _LANGUAGES[language]} if language in _LANGUAGES.keys() else _LANGUAGES
    for language in languages:
        try:
            languages[language]()
        except Exception as e:
            _LOG.info(f'Failed to collect issues status for {language}: {e}')
    Common.push_md_to_storage()


if __name__ == '__main__':
    main()
