import requests
import os

EXISTING_ROOT_PEM = requests.certs.where()

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
LOCAL_DEV_CERT = os.path.abspath(os.path.join(root_dir, 'eng', 'common', 'testproxy', 'dotnet-devcert.crt'))
COMBINED_FILENAME = os.path.basename(LOCAL_DEV_CERT).split(".")[0] + ".pem"
COMBINED_FOLDER = os.path.join(root_dir, '.certificate')
COMBINED_LOCATION = os.path.join(COMBINED_FOLDER, COMBINED_FILENAME)

def copy_cert_content():
    with open(LOCAL_DEV_CERT, 'r') as f:
        data = f.read()

    if not os.path.exists(COMBINED_FOLDER):
        os.mkdir(COMBINED_FOLDER)

    with open(COMBINED_LOCATION, 'w') as f:
        f.write(data)

def combine_cert_file():
    with open(EXISTING_ROOT_PEM, 'r') as f:
        content = f.readlines();

    with open(COMBINED_LOCATION, 'a') as f:
        f.writelines(content)

if __name__ == "__main__":
    copy_cert_content()
    combine_cert_file()

    print("Set the following certificate paths:")
    print("\tSSL_CERT_DIR={}".format(os.path.dirname(COMBINED_LOCATION)))
    print("\tREQUESTS_CA_BUNDLE={}".format(COMBINED_LOCATION))

    if os.getenv('TF_BUILD', False):
        print("##vso[task.setvariable variable=SSL_CERT_DIR]{}".format(os.path.dirname(COMBINED_LOCATION)))
        print("##vso[task.setvariable variable=REQUESTS_CA_BUNDLE]{}".format(COMBINED_LOCATION))
