import os.path
from unittest import mock

import pytest
from github.tests import Framework

from azure_devtools.ci_tools.bot_framework import BotHandler, order, build_from_issue_comment, build_from_issues

class BotFrameworkTest(Framework.TestCase):

    def setUp(self):
        self.maxDiff = None # Big diff to come
        self.recordMode = False  # turn to True to record
        self.tokenAuthMode = True
        self.replayDataFolder = os.path.join(os.path.dirname(__file__), "ReplayData")
        super(BotFrameworkTest, self).setUp()

    def test_webhook_data(self):
        github_token = self.oauth_token
        repo = self.g.get_repo("lmazuel/TestingRepo")

        fake_webhook = {
            'action': 'opened',  # What is the comment state?
            'repository': {
                'full_name': repo.full_name  # On what repo is this command?
            },
            'issue': {
                'number': 16,  # On what issue is this comment?
                'body': "@AutorestCI help"  # Message?
            },
            'sender': {
                'login': "lmazuel"  # Who wrote the command?
            },
        }
        webhook_data = build_from_issues(github_token, fake_webhook)
        assert webhook_data.text == "@AutorestCI help"
        assert webhook_data.issue.number == 16
        assert webhook_data.repo.full_name == repo.full_name

        fake_webhook = {
            'action': 'created',  # What is the comment state?
            'repository': {
                'full_name': repo.full_name  # On what repo is this command?
            },
            'issue': {
                'number': 16  # On what issue is this comment?
            },
            'sender': {
                'login': "lmazuel"  # Who wrote the command?
            },
            'comment': {
                'id': 365120206,
                'body': "@AutorestCI help"  # Message?
            }
        }
        webhook_data = build_from_issue_comment(github_token, fake_webhook)
        assert webhook_data.text == "@AutorestCI help"
        assert webhook_data.issue.number == 16
        assert webhook_data.repo.full_name == repo.full_name

    def test_bot_help(self):
        github_token = self.oauth_token
        repo = self.g.get_repo("lmazuel/TestingRepo")
        issue = repo.get_issue(16)

        class BotHelp:
            @order
            def command1(self, issue):
                pass
            @order
            def command2(self, issue):
                pass
            def notacommand(self):
                pass

        bot = BotHandler(BotHelp(), "AutorestCI", github_token)

        fake_webhook = {
            'action': 'opened',  # What is the comment state?
            'repository': {
                'full_name': issue.repository.full_name  # On what repo is this command?
            },
            'issue': {
                'number': issue.number,  # On what issue is this comment?
                'body': "@AutorestCI help"  # Message?
            },
            'sender': {
                'login': "lmazuel"  # Who wrote the command?
            },
        }

        response = bot.issues(fake_webhook)
        assert "this help message" in response["message"]
        assert "command1" in response["message"]
        assert "notacommand" not in response["message"]

        help_comment = list(issue.get_comments())[-1]
        assert "this help message" in help_comment.body
        assert "command1" in help_comment.body
        assert "notacommand" not in help_comment.body

        # Clean
        help_comment.delete()

    def test_bot_basic_command(self):
        github_token = self.oauth_token
        repo = self.g.get_repo("lmazuel/TestingRepo")
        issue = repo.get_issue(17)

        class BotCommand:
            @order
            def command1(self, issue, param1):
                assert issue.number == 17
                return "I did something with "+param1

        bot = BotHandler(BotCommand(), "AutorestCI", github_token)

        fake_webhook = {
            'action': 'opened',  # What is the comment state?
            'repository': {
                'full_name': issue.repository.full_name  # On what repo is this command?
            },
            'issue': {
                'number': issue.number,  # On what issue is this comment?
                'body': "@AutorestCI command1 myparameter"  # Message?
            },
            'sender': {
                'login': "lmazuel"  # Who wrote the command?
            },
        }

        response = bot.issues(fake_webhook)
        assert response["message"] == "I did something with myparameter"

        help_comment = list(issue.get_comments())[-1]
        assert "I did something with myparameter" in help_comment.body

        # Clean
        help_comment.delete()

    @mock.patch('traceback.format_exc')
    def test_bot_basic_failure(self, format_exc):
        format_exc.return_value = 'something to do with an exception'

        github_token = self.oauth_token
        repo = self.g.get_repo("lmazuel/TestingRepo")
        issue = repo.get_issue(18)

        class BotCommand:
            @order
            def command1(self, issue, param1):
                assert issue.number == 18
                raise ValueError("Not happy")

        bot = BotHandler(BotCommand(), "AutorestCI", github_token)

        fake_webhook = {
            'action': 'opened',  # What is the comment state?
            'repository': {
                'full_name': issue.repository.full_name  # On what repo is this command?
            },
            'issue': {
                'number': issue.number,  # On what issue is this comment?
                'body': "@AutorestCI command1 myparameter"  # Message?
            },
            'sender': {
                'login': "lmazuel"  # Who wrote the command?
            },
        }

        response = bot.issues(fake_webhook)
        assert response['message'] == 'Nothing for me or exception'

        help_comment = list(issue.get_comments())[-1]
        assert "something to do with an exception" in help_comment.body
        assert "```python" in help_comment.body

        # Clean
        help_comment.delete()


    def test_bot_unknown_command(self):
        github_token = self.oauth_token
        repo = self.g.get_repo("lmazuel/TestingRepo")
        issue = repo.get_issue(19)

        class BotCommand:
            pass

        bot = BotHandler(BotCommand(), "AutorestCI", github_token)

        fake_webhook = {
            'action': 'opened',  # What is the comment state?
            'repository': {
                'full_name': issue.repository.full_name  # On what repo is this command?
            },
            'issue': {
                'number': issue.number,  # On what issue is this comment?
                'body': "@AutorestCI command1 myparameter"  # Message?
            },
            'sender': {
                'login': "lmazuel"  # Who wrote the command?
            },
        }

        response = bot.issues(fake_webhook)
        assert "I didn't understand your command" in response['message']
        assert "command1 myparameter" in response['message']

        help_comment = list(issue.get_comments())[-1]
        assert "I didn't understand your command" in help_comment.body
        assert "command1 myparameter" in help_comment.body

        # Clean
        help_comment.delete()
