from collections import namedtuple
from functools import lru_cache
import logging
import os
import re

from github import Github, GithubException, UnknownObjectException

from .github_tools import (
    exception_to_github,
)

_LOGGER = logging.getLogger(__name__)


def order(function):
    function.bot_order = True
    return function

WebhookMetadata = namedtuple(
    'WebhookMetadata',
    ['repo', 'issue', 'text', 'comment']
)

def build_from_issue_comment(gh_token, body):
    """Create a WebhookMetadata from a comment added to an issue.
    """
    if body["action"] in ["created", "edited"]:
        github_con = Github(gh_token)
        repo = github_con.get_repo(body['repository']['full_name'])
        issue = repo.get_issue(body['issue']['number'])
        text = body['comment']['body']
        try:
            comment = issue.get_comment(body['comment']['id'])
        except UnknownObjectException:
            # If the comment has already disapeared, skip the command
            return None
        return WebhookMetadata(repo, issue, text, comment)
    return None

def build_from_issues(gh_token, body):
    """Create a WebhookMetadata from an opening issue text.
    """
    if body["action"] in ["opened", "edited"]:
        github_con = Github(gh_token)
        repo = github_con.get_repo(body['repository']['full_name'])
        issue = repo.get_issue(body['issue']['number'])
        text = body['issue']['body']
        comment = issue  # It's where we update the comment: in the issue itself
        return WebhookMetadata(repo, issue, text, comment)
    return None

@lru_cache()
def robot_name_from_env_variable():
    github_con = Github(os.environ["GH_TOKEN"])
    return github_con.get_user().login


class BotHandler:
    def __init__(self, handler, robot_name=None, gh_token=None):
        self.handler = handler
        self.gh_token = gh_token or os.environ["GH_TOKEN"]
        self.robot_name = robot_name or robot_name_from_env_variable()

    def _is_myself(self, body):
        return body['sender']['login'].lower() == self.robot_name.lower()

    def issue_comment(self, body):
        if self._is_myself(body):
            return {'message': 'I don\'t talk to myself, I\'m not schizo'}
        webhook_data = build_from_issue_comment(self.gh_token, body)
        return self.manage_comment(webhook_data)

    def issues(self, body):
        if self._is_myself(body):
            return {'message': 'I don\'t talk to myself, I\'m not schizo'}
        webhook_data = build_from_issues(self.gh_token, body)
        return self.manage_comment(webhook_data)

    def orders(self):
        """Return method tagged "order" in the handler.
        """
        return [order_cmd for order_cmd in dir(self.handler)
                if getattr(getattr(self.handler, order_cmd), "bot_order", False)]

    def manage_comment(self, webhook_data):
        if webhook_data is None:
            return {'message': 'Nothing for me'}
        # Is someone talking to me:
        message = re.search("@{} (.*)".format(self.robot_name), webhook_data.text, re.I)
        response = None
        if message:
            command = message.group(1)
            split_text = command.lower().split()
            orderstr = split_text.pop(0)
            if orderstr == "help":
                response = self.help_order()
            elif orderstr in self.orders():
                try:  # Reaction is fun, but it's preview not prod.
                      # Be careful, don't fail the command if we can't thumbs up...
                    webhook_data.comment.create_reaction("+1")
                except GithubException:
                    pass
                with exception_to_github(webhook_data.issue):  # Just in case
                    response = getattr(self.handler, orderstr)(webhook_data.issue, *split_text)
            else:
                response = "I didn't understand your command:\n```bash\n{}\n```\nin this context, sorry :(\n".format(
                    command
                )
                response += self.help_order()
            if response:
                webhook_data.issue.create_comment(response)
                return {'message': response}
        return {'message': 'Nothing for me or exception'}

    def help_order(self):
        orders = ["This is what I can do:"]
        for orderstr in self.orders():
            orders.append("- `{}`".format(orderstr))
        orders.append("- `help` : this help message")
        return "\n".join(orders)
