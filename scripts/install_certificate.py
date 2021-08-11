import requests
import os

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", ".."))
CERT_URL = "https://raw.githubusercontent.com/Azure/azure-sdk-tools/main/tools/test-proxy/docker/dev_certificate/dotnet-devcert.crt"
EXISTING_ROOT_PEM = requests.certs.where()
LOCAL_FILENAME = CERT_URL.split('/')[-1].split(".")[0] + ".pem"
LOCAL_LOCATION = os.path.join(root_dir, '.certificate', LOCAL_FILENAME)

def download_cert_file():
    content = requests.get(CERT_URL)

    if content.status_code == 200:
        with open(LOCAL_LOCATION, 'w') as f:
            f.write(content.text)

def combine_cert_file():
    with open(EXISTING_ROOT_PEM, 'r') as f:
        content = f.readlines();

    with open(LOCAL_LOCATION, 'a') as f:
        f.writelines(content)

if __name__ == "__main__":
    download_cert_file()
    combine_cert_file()

    print("Set the following certificate paths:")
    print("\tSSL_CERT_DIR={}".format(os.path.dirname(LOCAL_LOCATION)))
    print("\tREQUESTS_CA_BUNDLE={}".format(LOCAL_LOCATION))
    
    print("\nBe aware that REQUESTS_CA_BUNDLE should only be modified ")

