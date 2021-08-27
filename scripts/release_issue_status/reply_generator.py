import re

link_dict = {}


def begin_reply_generate(issue_object, rest_repo, readme_link):
    def weather_change_readme():
        # to see whether need change readme
        contents = str(rest_repo.get_contents(link_dict['readme_path']).decoded_content)
        pattern_tag = re.compile(r'tag: package-[\w+-.]+')
        package_tag = pattern_tag.search(contents).group()
        package_tag = package_tag.split(':')[1].strip()
        readme_python_contents = str(rest_repo.get_contents(link_dict['readme_python_path']).decoded_content)
        whether_multi_api = 'multi-api' in readme_python_contents
        whether_same_tag = package_tag == link_dict['readme_tag']
        whether_change_readme = not whether_same_tag or whether_multi_api and not 'MultiAPI' in labels
        return whether_change_readme

    # parse owner's comment and get links
    def get_links():
        comment_body = issue_object.body
        pattern_readme = re.compile(r'/specification/([\w-]+/)+readme.md')
        pattern_resource_manager = re.compile(r'/specification/([\w-]+/)+resource-manager')
        pattern_tag = re.compile(r'package-[\w+-.]+')
        readme_path = pattern_readme.search(readme_link).group()
        readme_tag = pattern_tag.search(comment_body).group()
        resource_manager = pattern_resource_manager.search(readme_link).group()
        link_dict['readme_path'] = readme_path
        link_dict['readme_python_path'] = readme_path[:readme_path.rfind('/')] + '/readme.python.md'
        link_dict['readme_tag'] = readme_tag
        link_dict['resource_manager'] = resource_manager

    def get_latest_pr_from_readme():
        commits = rest_repo.get_commits(path=link_dict['resource_manager'])
        latest_commit = [commit for commit in commits][0]
        latest_pr_brief = latest_commit.commit.message
        latest_pr_number = re.findall('\(\#[0-9]+\)', latest_pr_brief)
        latest_pr_number_int = []
        for number in latest_pr_number:
            number = int(re.search('\d+', number).group())
            latest_pr_number_int.append(number)
        latest_pr_number_int.sort()

        return latest_pr_number_int[-1]

    def latest_pr_parse():
        latest_pr = rest_repo.get_issue(latest_pr_number)
        latest_pr_comments = latest_pr.get_comments()
        b = [i for i in latest_pr_comments]
        for comment in latest_pr_comments:
            if '<h3>Swagger Generation Artifacts</h3>' in comment.body:
                return swagger_generator_parse(comment.body, issue_object, latest_pr_number)

    def swagger_generator_parse(context, issue_object, latest_pr_number):
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
            .format(issue_object.user.login, track1_info_model, track2_info_model, str(latest_pr_number))

        return info_model

    def reply_owner():
        issue_object.create_comment(reply_content)

    def add_label(label_name):
        if label_name not in labels:
            labels.append(label_name)
        issue_object.set_labels(*labels)

    get_links()
    whether_change_readme = weather_change_readme()
    # get issue labels
    labels = [label.name for label in issue_object.labels]

    if not whether_change_readme:
        # get the latest pr about service
        latest_pr_number = get_latest_pr_from_readme()
        reply_content = latest_pr_parse()
        reply_owner()
        add_label('P1')
    else:
        print('issue {} need config readme***********'.format(issue_object.number))
