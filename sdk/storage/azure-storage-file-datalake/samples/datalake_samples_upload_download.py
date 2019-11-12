import os
import random

from azure.storage.filedatalake import (
    DataLakeServiceClient,
)


def upload_download_sample(filesystem_client):
    # create a file before writing content to it
    file_name = "testfile"
    print("Creating a file named '{}'.".format(file_name))
    file_client = filesystem_client.create_file(file_name)

    # prepare the file content with 4KB of random data
    file_content = get_random_bytes(4*1024)

    # append data to the file
    # the data remain uncommitted until flush is performed
    print("Uploading data to '{}'.".format(file_name))
    file_client.append_data(data=file_content[0:1024], offset=0, length=1024)
    file_client.append_data(data=file_content[1024:2048], offset=1024, length=1024)
    file_client.append_data(data=file_content[2048:3072], offset=2048, length=1024)
    file_client.append_data(data=file_content[3072:4096], offset=3072, length=1024)

    # data is only committed when flush is called
    file_client.flush_data(len(file_content))

    # read the data back
    print("Downloading data from '{}'.".format(file_name))
    downloaded_bytes = file_client.read_file()

    # verify the downloaded content
    if file_content == downloaded_bytes:
        print("The downloaded data is equal to the data uploaded.")
    else:
        print("Something went wrong.")


# help method to provide random bytes to serve as file content
def get_random_bytes(size):
    rand = random.Random()
    result = bytearray(size)
    for i in range(size):
        result[i] = int(rand.random()*255)  # random() is consistent between python 2 and 3
    return bytes(result)


def run():
    account_name = os.getenv('STORAGE_ACCOUNT_NAME', "")
    account_key = os.getenv('STORAGE_ACCOUNT_KEY', "")

    # set up the service client with the credentials from the environment variables
    service_client = DataLakeServiceClient(account_url="{}://{}.dfs.core.windows.net".format(
        "https",
        account_name
    ), credential=account_key)

    # generate a random name for testing purpose
    fs_name = "testfs{}".format(random.randint(1, 1000))
    print("Generating a test filesystem named '{}'.".format(fs_name))

    # create the filesystem
    filesystem_client = service_client.create_file_system(file_system=fs_name)

    # invoke the sample code
    try:
        upload_download_sample(filesystem_client)
    finally:
        # clean up the demo filesystem
        filesystem_client.delete_file_system()


if __name__ == '__main__':
    run()
