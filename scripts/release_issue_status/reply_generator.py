import re


class ReplyGenerator(object):

    def __init__(self, issue_object, rest_repo):
        self.repo = rest_repo
        self.issue_object = issue_object
        self.labels = []
        self.comments = self.issue_object.get_comments()
        self.body = self.issue_object.body
        self.body_parse = {}
        self.rest_specs_object = None
        self.whether_change_readme = False
        self.whl_link = None
        self.changelog_content = None
        self.latest_pr_number = None

    def _whether_change_readme(self):
        self.rest_specs_object = self.repo
        contents = self.repo.get_contents(self.body_parse['readme_path'])
        contents = str(contents.decoded_content)
        pattern_tag = re.compile(r'tag: package-[\w+-.]+')
        package_tag = pattern_tag.search(contents).group()
        package_tag = package_tag.split(':')[1].strip()
        readme_python_contents = str(self.repo.get_contents(self.body_parse['readme_python_path']).decoded_content)
        whether_multi_api = 'multi-api' in readme_python_contents
        whether_same_tag = package_tag == self.body_parse['readme_tag']
        self.whether_change_readme = not (whether_same_tag and (not whether_multi_api or 'MultiAPI' in self.labels))

    def _body_parse(self):
        pattern_readme = re.compile(r'/specification/([\w-]+/)+readme.md')
        pattern_resource_manager = re.compile(r'/specification/([\w-]+/)+resource-manager')
        pattern_tag = re.compile(r'package-[\w+-.]+')
        readme_path = pattern_readme.search(self.body).group()
        readme_tag = pattern_tag.search(self.body).group()
        resource_manager = pattern_resource_manager.search(self.body).group()
        self.body_parse['readme_path'] = readme_path
        self.body_parse['readme_python_path'] = readme_path[:readme_path.rfind('/')] + '/readme.python.md'
        self.body_parse['readme_tag'] = readme_tag
        self.body_parse['resource_manager'] = resource_manager

    def _get_latest_pr_from_readme(self):
        commits = self.rest_specs_object.get_commits(path=self.body_parse['resource_manager'])
        latest_commit = [commit for commit in commits][0]
        latest_pr_brief = latest_commit.commit.message
        latest_pr_number = re.findall('\(\#[0-9]+\)', latest_pr_brief)
        latest_pr_number_int = []
        for number in latest_pr_number:
            number = int(re.search('\d+', number).group())
            latest_pr_number_int.append(number)
        latest_pr_number_int.sort()

        return latest_pr_number_int[-1]

    def _latest_pr_parse(self):
        latest_pr = self.rest_specs_object.get_issue(self.latest_pr_number)
        latest_pr_comments = latest_pr.get_comments()
        b = [i for i in latest_pr_comments]
        for comment in latest_pr_comments:
            if '<h3>Swagger Generation Artifacts</h3>' in comment.body:
                return self._swagger_generator_parse(comment.body)

    def _swagger_generator_parse(self, context):
        track1_info_model = ''
        try:
            if '<b> azure-sdk-for-python</b>' in context:
                pattern_python_t1 = re.compile('<b> azure-sdk-for-python</b>.+?</details>', re.DOTALL)
                python_t1 = re.search(pattern_python_t1, context).group()
                prttern_python_track1 = re.compile('<ul>\s+?<li>\s+?<a.+</ul>', re.DOTALL)
                python_track1_info = re.search(prttern_python_track1, python_t1).group()
                track1_info_model = '<details open><summary><b> python-track1</b></summary>{} </details>'.format(
                    python_track1_info)
        except Exception as e:
            print('track1 generate error')
        pattern_python = re.compile('<b> azure-sdk-for-python-track2</b>.+?</details>', re.DOTALL)
        python = re.search(pattern_python, context).group()
        # the way that reply not contains [Release SDK Changes]
        # pattern_python_track2 = re.compile('<ul>\s*?<li>\s*?<a.*</ul>', re.DOTALL)
        pattern_python_track2 = re.compile('<b>track2_.*</ul>', re.DOTALL)
        python_track2_info = re.search(pattern_python_track2, python).group()
        track2_info_model = '<details open><summary><b> python-track2</b></summary>{} </details>'.format(
            python_track2_info)
        info_model = 'hi @{} Please check the package whether works well and the changelog info is as below:\n' \
                     '{}\n{}\n' \
                     '\n* (The version of the package is only a temporary version for testing)\n' \
                     '\nhttps://github.com/Azure/azure-rest-api-specs/pull/{}\n' \
            .format(self.issue_object.user.login, track1_info_model, track2_info_model, str(self.latest_pr_number))

        return info_model

    def reply_owner(self, reply_content):
        self.issue_object.create_comment(reply_content)

    def add_label(self, label_name):
        if label_name not in self.labels:
            self.labels.append(label_name)
        self.issue_object.set_labels(*self.labels)

    def run(self):
        self.labels = [label.name for label in self.issue_object.labels]
        self._body_parse()
        self._whether_change_readme()
        if not self.whether_change_readme:
            self.latest_pr_number = self._get_latest_pr_from_readme()
            reply_content = self._latest_pr_parse()
            self.reply_owner(reply_content)
            self.add_label('P1')
        else:
            print('issue {} need config readme***********'.format(self.issue_object.number))
