import os
from colorama import init, Style, Fore
init()  # Initialize colorama for colored console output

from azure.identity import DefaultAzureCredential
from azure.computation import ComputeNodeAdministrationClient, OSChoiceEnum

def main():
    credentials = DefaultAzureCredential()
    client = ComputeNodeAdministrationClient(credentials, 'identifier')
    
    try:
        client.create_compute_node('Jorge', OSChoiceEnum.WINDOWS, 'Windows Node 1')
        client.create_compute_node('Alex', OSChoiceEnum.LINUX, 'Linux Node 1')

        windows_operation = client.begin_calculate_pi('Windows Node 1', 150)
        linux_operation = client.begin_calculate_pi('Linux Node 1', 150)


        print('Calculation percentage:')
        print('Windows done: ' + windows_operation.result().percent_complete())
        print('Linux done: ' + linux_operation.result().percent_complete()
)
