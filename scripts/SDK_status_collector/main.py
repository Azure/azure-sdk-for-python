import requests
import re
from lxml import etree
import lxml.html

DATE_DICT = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
             'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12', }
CLI_URL = 'https://github.com/azure/azure-cli/blob/0dab796a55ce6e600200d15c324d57100db38cfa/' \
          'src/azure-cli/setup.py'
BASE_URL = 'https://github.com'
SDK_URL = "https://github.com/Azure/azure-rest-api-specs/tree/master/specification"
CLI_DICT = {}


class PyPIClient:
    def __init__(self, host="https://pypi.org", package_name='', track_config='',
                 readme_link='', rm_link='', cli_version=''):
        self._host = host
        self._session = requests.Session()
        self._package_name = package_name
        self.version_date_dict = {}
        self.weather_track2 = None
        self.track1_ga = 'NO'
        self.track1_latest = 'NA'
        self.track2_ga = 'NO'
        self.track2_latest = 'NA'
        self.pypi_link = None
        self.track_config = track_config
        self.readme_link = readme_link
        self.rm_link = rm_link
        self.cli_version = cli_version
        self.weather_pypi = True
        self.bot_warning = ''
        self.service_not_to_pypi = []

    def project_html(self):
        self.pypi_link = "{host}/pypi/{project_name}".format(
            host=self._host,
            project_name=self._package_name
        )
        response = self._session.get(self.pypi_link + "/#history")

        # response.raise_for_status()
        return response

    def get_release_info(self, response, xpath, type):
        text = response.text
        parse_text = lxml.etree.HTML(text)
        release_info = parse_text.xpath(xpath)
        strip_info = []
        for info in release_info:
            info = info.strip()
            if type == 'date':
                info = info.replace(',', '').split(' ')
                info = info[2] + '/' + DATE_DICT[info[0]] + '/' + info[1]
            if not len(info) == 0:
                strip_info.append(info)

        return strip_info

    def get_release_dict(self, response):
        version_list = self.get_release_info(response, xpath='//p[@class="release__version"]/text()', type='version')
        self.version_handler(version_list)
        data_list = self.get_release_info(response, xpath='//p[@class="release__version-date"]/time/text()',
                                          type='date')
        self.version_date_dict = dict(zip(version_list, data_list))
        self.version_date_dict['NA'] = 'NA'

    def write_to_list(self):
        response = self.project_html()
        if 199 < response.status_code < 400:
            self.get_release_dict(response)
            self.bot_analysis()
            return '{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(self._package_name,
                                                                  self.pypi_link,
                                                                  self.track1_latest,
                                                                  self.version_date_dict[self.track1_latest],
                                                                  self.track1_ga,
                                                                  self.track2_latest,
                                                                  self.track2_ga,
                                                                  self.version_date_dict[self.track2_latest],
                                                                  self.cli_version,
                                                                  self.track_config,
                                                                  self.bot_warning,
                                                                  self.rm_link)
        else:
            self.pypi_link = 'NA'
            self.weather_pypi = False
        return

    def version_handler(self, version_list):
        ga_re = re.compile(r'[A-Za-z]')
        version_index = 0
        versions = list(reversed(version_list))
        for version in versions:
            if 'b1' in version and self.weather_track2 is None:
                self.weather_track2 = version
                if self.cli_version != 'NA':
                    if int(self.cli_version.split('.')[0]) >= int(version.split('.')[0]):
                        self.cli_version = 'track2_' + self.cli_version
                    else:
                        self.cli_version = 'track1_' + self.cli_version
                if version_index != 0:
                    self.track1_latest = versions[version_index - 1]
                self.track2_latest = versions[-1]
                if not re.findall(ga_re, self.track1_latest) and len(self.track1_latest) != 0 and int(
                        self.track1_latest.split('.')[0]) > 0:
                    self.track1_ga = 'YES'
                if not re.findall(ga_re, self.track2_latest):
                    self.track2_ga = 'YES'
                break
            version_index += 1
        if self.weather_track2 is None:
            if self.cli_version != 'NA':
                self.cli_version = 'track1_' + self.cli_version
            self.track1_latest = versions[-1]
            if not re.findall(ga_re, self.track1_latest) and len(self.track1_latest) != 0 and int(
                    self.track1_latest.split('.')[0]) > 0:
                self.track1_ga = 'YES'

    def bot_analysis(self):
        if self.readme_link == 'NA':
            self.bot_warning += 'The readme.python.md has not been created.  '
        if self.cli_version != 'NA':
            cli_version = int(self.cli_version.split('_')[1].split('.')[0])
            if self.weather_track2 is not None:
                weather_track2 = int(self.weather_track2.split('.')[0])
                if cli_version >= weather_track2 and self.track_config == 'both':
                    self.bot_warning += 'The cli using track2 now but readme.python still have track1‘s config'


def get_sdk_info(_sdk_info):
    _sdk_names = []
    for package in _sdk_info[1:]:
        if ',' in package:
            package = package.split(',')
            sdk_name = package[0].strip()
            if sdk_name in CLI_DICT.keys():
                cli_version = CLI_DICT[sdk_name]
            else:
                cli_version = 'NA'
            track_config = package[1].strip()
            readme_link = package[2].strip()
            rm_link = package[3].strip()
            pypi_ins = PyPIClient(package_name=sdk_name, track_config=track_config,
                                  readme_link=readme_link, rm_link=rm_link, cli_version=cli_version)
            text_to_write = pypi_ins.write_to_list()
            if pypi_ins.weather_pypi is True:
                all_sdk_status.append(text_to_write)
            else:
                service_not_to_pypi.append(pypi_ins._package_name + '\n,')
        else:
            _sdk_names.append(package.strip())
    return _sdk_names


def write_to_csv(sdk_status_list, csv_name):
    with open(csv_name, 'w') as file_out:
        file_out.write('package name,'
                       'pypi link,'
                       'latest track1 version,'
                       'release date,'
                       'track1 GA,'
                       'latest track2 version,'
                       'track2 GA,'
                       'release date,'
                       'cli dependency,'
                       'readme config,'
                       'bot advice,'
                       'readme link\n')
        file_out.writelines(
            [package for package in sorted(sdk_status_list, key=lambda x: x.split(',')[10], reverse=True)])


def get_cli_info():
    cli_lines = project_html(CLI_URL).xpath('//table[@class="highlight tab-size js-file-line-container"]//text()')
    for line in cli_lines:
        if 'azure-mgmt-' in line:
            line = line[1:-1]
            if '==' in line:
                line = line.split('==')
                CLI_DICT[line[0]] = line[1]
            elif '~=' in line:
                line = line.split('~=')
                CLI_DICT[line[0]] = line[1]


def project_html(url):
    response = requests.Session().get(url)
    response.encoding = 'gbk'
    text = response.text
    parse_result = lxml.etree.HTML(text)
    return parse_result


def sdk_collector_rest():
    sdk_name_re = re.compile(r'azure-mgmt-[a-z]+-*([a-z])+')
    resource_manager = []
    sdk_hrefs = project_html(SDK_URL).xpath('//div[@class="js-details-container Details"]/div/div/'
                                            'div[@class="flex-auto min-width-0 col-md-2 mr-3"]//a/@href')
    for href in sdk_hrefs:
        readme_python = None
        track_config = []
        package_name = ''
        if 'resource-manager' not in href:
            href = href + '/resource-manager'
        href = BASE_URL + href
        html_text = project_html(href)
        resource_manager_folders = html_text.xpath('//div[@class="js-details-container Details"]/div/div/'
                                                   'div[@class="flex-auto min-width-0 col-md-2 mr-3"]//a/text()')
        for resource_manager_folder in resource_manager_folders:
            if resource_manager_folder == 'readme.python.md':
                readme_python = href + '/readme.python.md'
        readme_text = html_text.xpath('//div[@class="Box-body px-5 pb-5"]/article//text()')
        for line in readme_text:
            if line == 'azure-sdk-for-python':
                track_config.append('track1')
            if line == 'azure-sdk-for-python-track2':
                track_config.append('track2')
            if readme_python is None and sdk_name_re.search(line) is not None and package_name == '':
                package_name = sdk_name_re.search(line).group()
        if len(track_config) == 2:
            track_config = 'both'
        elif len(track_config) > 2:
            track_config = 'Rule error'
        elif len(track_config) == 1:
            track_config = track_config[0]
        elif len(track_config) == 0:
            track_config = 'NA'
        if readme_python is not None:
            readme_python_html_text = project_html(readme_python)
            readme_python_text = readme_python_html_text.xpath('//div[@id="readme"]/article//text()')
            for text in readme_python_text:
                if sdk_name_re.search(text) is not None:
                    package_name = sdk_name_re.search(text).group()

        if package_name != '':
            if readme_python is None:
                readme_python = 'NA'
            resource_manager.append('{},{},{},{}\n'.format(package_name,
                                                           track_config,
                                                           readme_python,
                                                           str(href)))

    return resource_manager


if __name__ == '__main__':
    get_cli_info()
    all_sdk_status = []
    service_not_to_pypi = []
    sdk_info = sdk_collector_rest()
    sdk_names = get_sdk_info(sdk_info)
    write_to_csv(all_sdk_status, 'sdk_status_collector.csv')

    # #  services which have not been published to pypi
    # with open('service_not_to_pypi.csv', 'w') as file_out:
    #     file_out.writelines(package for package in service_not_to_pypi)
