# coding=utf-8
import os
import subprocess as sp
import time
from pypi_tools.pypi import PyPIClient

package_info = [('powerbiembedded', 'powerbiembedded'), ('signalr', 'signalr'), ('attestation', 'attestation'),
                ('managementpartner', 'managementpartner'), ('network', 'dns'), ('mobilenetwork', 'mobilenetwork'),
                ('streamanalytics', 'streamanalytics'), ('reservations', 'reservations'),
                ('databoxedge', 'databoxedge'), ('media', 'media'), ('resources', 'resourcegraph'),
                ('datamigration', 'datamigration'), ('timeseriesinsights', 'timeseriesinsights'),
                ('managementgroups', 'managementgroups'), ('portal', 'portal'), ('cdn', 'cdn'),
                ('kubernetesconfiguration', 'kubernetesconfiguration'), ('servicebus', 'servicebus'),
                ('resourcemover', 'resourcemover'), ('storagepool', 'storagepool'), ('healthbot', 'healthbot'),
                ('mixedreality', 'mixedreality'), ('trafficmanager', 'trafficmanager'),
                ('connectedvmware', 'connectedvmware'), ('storage', 'storagecache'),
                ('desktopvirtualization', 'desktopvirtualization'), ('deviceupdate', 'deviceupdate'),
                ('quota', 'quota'), ('confidentialledger', 'confidentialledger'), ('compute', 'vmwarecloudsimple'),
                ('billing', 'billing'), ('servicefabric', 'servicefabric'), ('eventhub', 'eventhub'),
                ('videoanalyzer', 'videoanalyzer'), ('redisenterprise', 'redisenterprise'),
                ('customproviders', 'customproviders'), ('recoveryservices', 'recoveryservicessiterecovery'),
                ('recoveryservices', 'recoveryservices'), ('rdbms', 'rdbms'), ('healthcareapis', 'healthcareapis'),
                ('oep', 'oep'), ('hybridkubernetes', 'hybridkubernetes'), ('apimanagement', 'apimanagement'),
                ('cognitiveservices', 'cognitiveservices'), ('alertsmanagement', 'alertsmanagement'),
                ('chaos', 'chaos'), ('netapp', 'netapp'), ('maintenance', 'maintenance'), ('purview', 'purview'),
                ('machinelearning', 'guestconfig'), ('aks', 'devspaces'), ('consumption', 'consumption'),
                ('keyvault', 'keyvault'), ('webpubsub', 'webpubsub'), ('authorization', 'authorization'),
                ('resources', 'resource'), ('changeanalysis', 'changeanalysis'), ('orbital', 'orbital'),
                ('extendedlocation', 'extendedlocation'),
                ('servicefabricmanagedclusters', 'servicefabricmanagedclusters'), ('azurestack', 'azurestack'),
                ('appconfiguration', 'appconfiguration'), ('network', 'privatedns'), ('digitaltwins', 'digitaltwins'),
                ('iothub', 'iothubprovisioningservices'), ('compute', 'imagebuilder'),
                ('machinelearning', 'machinelearningcompute'), ('databox', 'databox'),
                ('storage', 'storageimportexport'), ('rdbms', 'rdbms'), ('testbase', 'testbase'),
                ('iothub', 'iotcentral'), ('serialconsole', 'serialconsole'), ('support', 'support'),
                ('hybridnetwork', 'hybridnetwork'), ('sql', 'sql'), ('maps', 'maps'), ('hanaonazure', 'hanaonazure'),
                ('automanage', 'automanage'), ('azurearcdata', 'azurearcdata'), ('agrifood', 'agrifood'),
                ('labservices', 'labservices'), ('rdbms', 'rdbms'), ('edgeorder', 'edgeorder'),
                ('deploymentmanager', 'deploymentmanager'), ('hdinsight', 'hdinsight'),
                ('communication', 'communication'), ('servicelinker', 'servicelinker'),
                ('securityinsight', 'securityinsight'), ('appservice', 'web'), ('logic', 'logic'),
                ('azurestackhci', 'azurestackhci'), ('peering', 'peering'),
                ('marketplaceordering', 'marketplaceordering'), ('resources', 'msi'), ('compute', 'avs'),
                ('advisor', 'advisor'), ('containerinstance', 'containerinstance'), ('eventgrid', 'eventgrid'),
                ('automation', 'automation'), ('elastic', 'elastic'), ('dataprotection', 'dataprotection'),
                ('containerservice', 'containerservice'), ('logz', 'logz'), ('dnsresolver', 'dnsresolver'),
                ('kusto', 'kusto'), ('subscription', 'subscription'), ('quantum', 'quantum'),
                ('policyinsights', 'policyinsights'), ('security', 'security'),
                ('machinelearning', 'machinelearningservices'), ('baremetalinfrastructure', 'baremetalinfrastructure'),
                ('loganalytics', 'loganalytics'), ('commerce', 'commerce'), ('costmanagement', 'costmanagement'),
                ('app', 'app'), ('workloadmonitor', 'workloadmonitor'), ('managedservices', 'managedservices'),
                ('powerbidedicated', 'powerbidedicated'), ('compute', 'compute'),
                ('containerregistry', 'containerregistry'), ('network', 'network'),
                ('loadtestservice', 'loadtestservice'), ('hybridcompute', 'hybridcompute'), ('batch', 'batch'),
                ('scheduler', 'scheduler'), ('databricks', 'databricks'), ('synapse', 'synapse'), ('search', 'search'),
                ('resourcehealth', 'resourcehealth'), ('storage', 'storage'), ('iothub', 'iothub'),
                ('sql', 'sqlvirtualmachine'), ('devtestlabs', 'devtestlabs'), ('datadog', 'datadog'),
                ('recoveryservices', 'recoveryservicesbackup'), ('confluent', 'confluent'),
                ('datafactory', 'datafactory'), ('operationsmanagement', 'operationsmanagement'),
                ('appplatform', 'appplatform'), ('datashare', 'datashare'), ('network', 'frontdoor'),
                ('rdbms', 'rdbms'), ('redhatopenshift', 'redhatopenshift'), ('notificationhubs', 'notificationhubs'),
                ('monitor', 'monitor'), ('applicationinsights', 'applicationinsights'), ('fluidrelay', 'fluidrelay'),
                ('relay', 'relay'), ('resourceconnector', 'resourceconnector'), ('redis', 'redis'),
                ('storage', 'storagesync'), ('cosmos', 'cosmosdb'), ('botservice', 'botservice')
                ]

def find_report_name(result):
    pattern = 'written to'
    merged = 'merged_report'
    for line in result:
        idx = line.find(pattern)
        idx1 = line.find(merged)
        if idx > 0 and idx1 > 0:
            return "_/" + line[idx + len(pattern):].replace(" ", "")

    for line in result:
        idx = line.find(pattern)
        if idx > 0:
            return "_/" + line[idx + len(pattern):].replace(" ", "")

    return ''

def create_foldor(name):
    if not os.path.exists(name):
        os.mkdir(name)
        print("create successful")
    else:
        print("foldor has been created")

def write_txt(foldor, text_name, text, version1, version2):
    foldor_path = r'{0}\\'.format(foldor)
    path = foldor_path + text_name + " " + version1 + "-" + version2 + r".txt"
    file = open(path, "w", encoding="utf-8")
    file.write(text)
    print("txt create successful")
    file.close()

def create_code_report(cmd):
    info = sp.Popen(cmd,
                    stderr=sp.STDOUT,
                    stdout=sp.PIPE,
                    universal_newlines=True,
                    cwd=None,
                    shell=False,
                    env=None,
                    encoding="utf-8",
                    )

    output_buffer = []
    for line in info.stdout:
        output_buffer.append(line.rstrip())
    info.wait()
    info_output = "\n".join(output_buffer)
    return info_output.split('\n')

if __name__ == '__main__':
    env = os.getcwd()
    docker_path = env.split("\scripts")[0]
    sp.call(fr"docker create -it --rm -h Change_log --name Change_log -v {docker_path}:/_ l601306339/autorest")
    sp.call("docker start Change_log")
    sp.call(f'docker exec -it Change_log /bin/bash -c  "python _/scripts/dev_setup.py -p azure-core"  ')
    for package in package_info:
        package_name = package[0]
        package_path = package[1]

        client = PyPIClient()
        versions = [str(v) for v in client.get_ordered_versions(f"azure-mgmt-{package_path}")]
        if len(versions) >= 2:
            version = versions[-2]
            last_version = versions[-1]
        else:
            version = versions[-1]
            last_version = versions[-1]

        cmd_cl1 = fr'docker exec -it Change_log /bin/bash -c "cd _/ && python -m packaging_tools.code_report  azure-mgmt-{package_path} --version={last_version}"'
        cmd_cl2 = fr'docker exec -it Change_log /bin/bash -c "cd _/ && python -m packaging_tools.code_report azure-mgmt-{package_path} --version={version}"'

        last_info = create_code_report(cmd_cl1)
        info = create_code_report(cmd_cl2)
        last_route = find_report_name(last_info)
        route = find_report_name(info)

        result_text = sp.getoutput(
            fr'docker exec -it Change_log /bin/bash -c "python -m packaging_tools.change_log {route} {last_route}"')
        print(result_text)

        change_log_foldor_path = env + r"\Change_Log"
        create_foldor(change_log_foldor_path)
        write_txt(change_log_foldor_path, package_path, result_text, last_version, version)

        time.sleep(10)
    sp.call(f'docker exec -it Change_log /bin/bash -c "exit"')
    sp.call(f'docker stop Change_log')
