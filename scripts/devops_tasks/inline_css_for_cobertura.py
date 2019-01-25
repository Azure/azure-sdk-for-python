import os
import bs4

COVERAGE_REPORT_DIR = 'htmlcov/'
COVERAGE_REPORT = os.path.join(COVERAGE_REPORT_DIR, 'index.html')

def embed_css_in_html_file(html_file, css_dir):
    with open(html_file, 'r') as f:
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
        
    with open(html_file, 'w') as f:
        f.write(str(soup))

if __name__ == '__main__':
    for file in os.listdir(COVERAGE_REPORT_DIR):
        if file.endswith(".html"):
            print("Embedding CSS in {}".format(file))
            embed_css_in_html_file(os.path.join(COVERAGE_REPORT_DIR, file), COVERAGE_REPORT_DIR)
