import datetime

import requests
from bs4 import BeautifulSoup


def auto_close_issue(sdk_repo, item):
    issue_number, package_name = item.issue_object.number, item.package
    issue_info = sdk_repo.get_issue(number=issue_number)
    issue_author = issue_info.user.login
    last_comment = list(issue_info.get_comments())[-1]
    last_comment_date = last_comment.created_at
    last_version, last_time = get_last_released_date(package_name)
    if last_time and last_time > last_comment_date:
        comment = f'Hi @{issue_author}, pypi link: https://pypi.org/project/{package_name}/{last_version}/'
        issue_info.create_comment(body=comment)
        issue_info.edit(state='closed')
        item.labels.append('auto-closed')
        item.issue_object.set_labels(*item.labels)
        print(f"issue number：{issue_number} has been closed!")


def get_last_released_date(package_name):
    pypi_link = f'https://pypi.org/project/{package_name}/#history'
    res = requests.get(pypi_link)
    soup = BeautifulSoup(res.text, 'html.parser')
    # find top div from <div class="release-timeline">
    try:
        package_info = soup.select('div[class="release-timeline"]')[0].find_all('div')[0]
        last_version_mix = package_info.find_all('p', class_="release__version")[0].contents[0]
    except IndexError as e:
        return '', ''
    last_version = last_version_mix.replace(' ', '').replace('\n', '')
    last_version_date_str = package_info.time.attrs['datetime'].split('+')[0]
    last_version_date = datetime.datetime.strptime(last_version_date_str, '%Y-%m-%dT%H:%M:%S')
    return last_version, last_version_date
