from __future__ import print_function
import os
import bs4
import io
import sys
import shutil

COVERAGE_REPORT_DIR = 'htmlcov/'
COVERAGE_REPORT = os.path.join(COVERAGE_REPORT_DIR, 'index.html')

def __str_version_handler(string):
    if sys.version_info >= (3, 0):
        return str(string)
    else:
        return unicode(string)

def embed_css_in_html_file(html_file, css_dir):
    with io.open(html_file, 'r', encoding='utf-8') as f:
        soup = bs4.BeautifulSoup(f.read(), "html.parser")

    stylesheets = soup.findAll("link", {"rel": "stylesheet"})
    for sheet in stylesheets:

        # insert a new style tag where the old linkrel tag was
        tag = soup.new_tag('style')
        tag['type'] = 'text/css'

        # grab the href to the CSS file and read it all
        css_file = sheet["href"]
        with open(os.path.join(css_dir, css_file), 'r') as f:
            c = bs4.element.NavigableString(f.read())

        # insert the contents of the stylesheet into the style tag we just created
        tag.insert(0, c)

        # then replace the sheet tag with the data from the stylesheet 
        sheet.replaceWith(tag)
    
    with io.open(html_file, 'w', encoding='utf-8') as f:
        f.write(__str_version_handler(soup))

def clean_index(html_file):
    with io.open(html_file, 'r', encoding='utf-8') as f:
        soup = bs4.BeautifulSoup(f.read(), "html.parser")

    # remove all links to the files that don't exist anymore
    for a in soup.findAll('a'):
        a.replaceWithChildren()

    # embedded CSS corrupts the sort indicator image. Javascript doesn't work in the devops display anyway. Removing the class
    module_title = soup.find('th', class_='headerSortDown')["class"].remove('headerSortDown')

    # remove input filter
    input_filter = soup.find(id= 'filter')
    input_filter.decompose()

    # remove keyboard icon
    keyboard_icon = soup.find(id='keyboard_icon')
    keyboard_icon.decompose()

    # write final results
    with io.open(html_file, 'w', encoding='utf-8') as f:
        f.write(__str_version_handler(soup))

if __name__ == '__main__':
    for file in os.listdir(COVERAGE_REPORT_DIR):
        name, ext = os.path.splitext(os.path.basename(file.lower()))
        if ext == ".html":
            if name == "index":
                print("Cleaning index in {}".format(file))
                clean_index(os.path.join(COVERAGE_REPORT_DIR, file))
                print("Embedding CSS in {}".format(file))
                embed_css_in_html_file(os.path.join(COVERAGE_REPORT_DIR, file), COVERAGE_REPORT_DIR)
            else:
                os.remove(os.path.join(COVERAGE_REPORT_DIR, file))


