import re


def update_issue_body(sdk_repo, rest_repo, issue_number):
    # Get Issue Number
    issue_info = sdk_repo.get_issue(number=issue_number)
    issue_body = issue_info.body
    issue_body_list = [i for i in issue_body.split("\n") if i]
    # Get the link and readme tag in issue body
    link, readme_tag = '', ''
    for row in issue_body_list:
        if 'link' in row.lower():
            link = row.split(":", 1)[-1].strip()
        if 'readme tag' in row.lower():
            readme_tag = row.split(":", 1)[-1].strip()
        if link and readme_tag:
            break

    if link.count('https') > 1:
        link = link.split(']')[0]
        link = link.replace('[', "").replace(']', "").replace('(', "").replace(')', "")

    package_name, readme_link, output_folder = get_pkname_and_readme_link(rest_repo, link)
    
    # Check readme tag format
    if 'package' not in readme_tag:
        readme_tag = 'package-{}'.format(readme_tag)
        issue_body_list.insert(0, f'Readme Tag: {readme_tag}')

    issue_body_list.insert(0, f'\n{readme_link.replace("/readme.md", "")}')
    issue_body_list.insert(1, package_name)
    issue_body_up = ''
    for raw in issue_body_list:
        if raw == '---\r' or raw == '---':
            issue_body_up += '\n'
        issue_body_up += raw + '\n'

    issue_info.edit(body=issue_body_up)
    return package_name, readme_link, output_folder
        

def get_pkname_and_readme_link(rest_repo, link):
    # change commit link to pull json link(i.e. https://github.com/Azure/azure-rest-api-specs/commit/77f5d3b5d2fbae17621ea124485788f496786758#diff-708c2fb843b022cac4af8c6f996a527440c1e0d328abb81f54670747bf14ab1a)
    pk_name = ''
    if 'commit' in link:
        commit_sha = link.split('commit/')[-1]
        commit = rest_repo.get_commit(commit_sha)
        link = commit.files[0].blob_url
        link = re.sub('blob/(.*?)/specification', 'blob/main/specification', link)

    # if link is a pr, it can get both pakeage name and readme link.
    if 'pull' in link:
        pr_number = int(link.replace("https://github.com/Azure/azure-rest-api-specs/pull/", "").strip('/'))

        # Get Readme link
        pr_info = rest_repo.get_pull(number=pr_number)
        pk_url_name = set()
        for pr_changed_file in pr_info.get_files():
            contents_url = pr_changed_file.contents_url
            if '/resource-manager' in contents_url:
                try:
                    pk_url_name.add(re.findall(r'/specification/(.*?)/resource-manager/', contents_url)[0])
                except Exception as e:
                    continue
                if len(pk_url_name) > 1:
                    print("\nexists multiple package names: {}, {} \n".format(pk_url_name, pk_url_name1))
                    raise Exception('Not find readme link, because it exists multiple package names')

        readme_link = 'https://github.com/Azure/azure-rest-api-specs/blob/main/specification/{}/' \
                      'resource-manager/readme.python.md'.format(list(pk_url_name)[0])


    # if link is a rest url(i.e. https://github.com/Azure/azure-rest-api-specs/blob/main/specification/xxx/resource-manager/readme.python.md)
    elif '/resource-manager' not in link:
        # (i.e. https://github.com/Azure/azure-rest-api-specs/tree/main/specification/xxxx)
        readme_link = link + '/resource-manager/readme.python.md'
    else:
        readme_link = link.split('/resource-manager')[0] + '/resource-manager/readme.python.md'
    # get the package name by readme link
    readme_link_part = '/specification' + readme_link.split('/specification')[-1]
    readme_contents = str(rest_repo.get_contents(readme_link_part).decoded_content)
    pk_name = re.findall(r'package-name: (.*?)\\n', readme_contents)[0]
    out_folder = re.findall(r'\$\(python-sdks-folder\)/(.*?)/azure-', readme_contents)[0]
    readme_link = readme_link.replace('python.', '')

    return pk_name, readme_link, out_folder


def find_readme_and_output_folder(sdk_repo, rest_repo, issue_number):
    # Get Issue Number
    issue_info = sdk_repo.get_issue(number=issue_number)
    issue_body = issue_info.body
    issue_body_list = issue_body.split("\n")
    for row in issue_body_list:
        if 'resource-manager' in row:
            readme_link = '{}/readme.md'.format(row.strip("\r"))
            # Get output folder from readme.python.md
            readme_python_link = readme_link.split('/resource-manager')[0] + '/resource-manager/readme.python.md'
            readme_python_link_part = '/specification' + readme_python_link.split('/specification')[-1]
            readme_contents = str(rest_repo.get_contents(readme_python_link_part).decoded_content)
            output_folder = re.findall(r'\$\(python-sdks-folder\)/(.*?)/azure-', readme_contents)[0]

            return readme_link, output_folder
    raise Exception('Not find readme link,please check')

