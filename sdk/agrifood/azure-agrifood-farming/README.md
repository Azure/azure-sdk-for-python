# Azure FarmBeats client library for Python
FarmBeats is a B2B PaaS offering from Microsoft that makes it easy for AgriFood companies to build intelligent digital agriculture solutions on Azure. FarmBeats allows users to acquire, aggregate, and process agricultural data from various sources (farm equipment, weather, satellite) without the need to invest in deep data engineering resources.  Customers can build SaaS solutions on top of FarmBeats and leverage first class support for model building to generate insights at scale.

Use FarmBeats client library for Python to do the following.

- Create & update farmers, farms, fields, seasonal fields and boundaries.
- Ingest satellite and weather data for areas of interest.
- Ingest farm operations data covering tilling, planting, harvesting and application of farm inputs.

[Source code][source_code] | [Package (PyPi)][pypi-package] | [API reference documentation][api_docs] | [Product documentation][product_docs] | [Changelog][change_log]

## Getting started

### Prerequisites

To use this package, you must have:
- Azure subscription - [Create a free account][azure_subscription]
- Azure FarmBeats resource - [Install FarmBeats][install_farmbeats]
- 3.6 or later - [Install Python][python]

### Install the package

Install the Azure FarmBeats client library for Python with [pip][pip]:

```bash
pip install azure-agrifood-farming
```

### Authenticate the client

To use an [Azure Active Directory (AAD) token credential][authenticate_with_token],
provide an instance of the desired credential type obtained from the
[azure-identity][azure_identity_credentials] library.

To authenticate with AAD, you must first [pip][pip] install [`azure-identity`][azure_identity_pip] and
enable AAD authentication on your FarmBeats resource. If you followed the [installation docs][install_farmbeats] when creating the FarmBeats
resource, this is already covered.

After setup, you can choose which type of [credential][azure_identity_credentials] from azure.identity to use.
As an example, [DefaultAzureCredential][default_azure_credential]
can be used to authenticate the client:

Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET

Use the returned token credential to authenticate the client:

```python
from azure.agrifood.farming import FarmBeatsClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = FarmBeatsClient(endpoint="https://<my-account-name>.farmbeats.azure.net", credential=credential)
```

## Key concepts
Basic understanding of below terms will help to get started with FarmBeats client library.

### [Farm Hierarchy][farm_hierarchy]
Farm hierarchy is a collection of below entities.
- Farmer - is the custodian of all the agronomic data.
- Farm - is a logical collection of fields and/or seasonal fields. They do not have any area associated with them.
- Field - is a multi-polygon area. This is expected to be stable across seasons.
- Seasonal field - is a multi-polygon area. To define a seasonal boundary we need the details of area (boundary), time (season) and crop. New seasonal fields are expected to be created for every growing season.
- Boundary - is the actual multi-polygon area expressed as a geometry (in geojson). It is normally associated with a field or a seasonal field. Satellite, weather and farm operations data is linked to a boundary.
- Cascade delete - Agronomic data is stored hierarchically with farmer as the root. The hierarchy includes Farmer -> Farms -> Fields -> Seasonal Fields -> Boundaries -> Associated data (satellite, weather, farm operations). Cascade delete refers to the process of deleting any node and its subtree.

### [Scenes][scenes]
Scenes refers to images normally ingested using satellite APIs. This includes raw bands and derived bands (Ex: NDVI). Scenes may also include spatial outputs of an inference or AI/ML model (Ex: LAI).

### [Farm Operations][farm_operations_docs]
Fam operations includes details pertaining to tilling, planting, application of pesticides & nutrients, and harvesting. This can either be manually pushed into FarmBeats using APIs or the same information can be pulled from farm equipment service providers like John Deere.


## Examples

### Create a Farmer
Once you have authenticated and created the client object as shown in the [Authenticate the client](#authenticate-the-client)
section, you can create a farmer within the FarmBeats resource like this:

```python
from azure.identity import DefaultAzureCredential
from azure.agrifood.farming import FarmBeatsClient
from azure.agrifood.farming.models import Farmer

credential = DefaultAzureCredential()
client = FarmBeatsClient(endpoint="https://<my-account-name>.farmbeats.azure.net", credential=credential)

farmer = client.farmers.create_or_update(
    farmer_id="farmer-1",
    farmer=Farmer(
        name="Contoso Farmer",
        description="Your custom farmer description here",
        status="Active",
        properties={
            "your-custom-key": "queryable value",
        }
    )
)
```

### Create a Farm


```python
from azure.identity import DefaultAzureCredential
from azure.agrifood.farming import FarmBeatsClient
from azure.agrifood.farming.models import Farm

credential = DefaultAzureCredential()
client = FarmBeatsClient(endpoint="https://<my-account-name>.farmbeats.azure.net", credential=credential)

farmer_id = "farmer-1" # Using farmer from previous example

farm = client.farms.create_or_update(
    farmer_id=farmer_id,
    farm_id="farm-1",
    farm=Farm(
        name="Contoso Westlake Farm",
        properties={
            "location": "Westlake",
            "country": "USA"
        }
    )
)
```

### Create a Season

Creating a Season object, spanning from April to August of 2021.

```python
from azure.identity import DefaultAzureCredential
from azure.agrifood.farming import FarmBeatsClient
from azure.agrifood.farming.models import Season

from isodate.tzinfo import Utc
from datetime import datetime

credential = DefaultAzureCredential()
client = FarmBeatsClient(endpoint="https://<my-account-name>.farmbeats.azure.net", credential=credential)

season = client.seasons.create_or_update(
    season_id="season-summer-2021",
    season=Season(
        start_date_time=datetime(2021, 4, 1, tzinfo=Utc()),
        end_date_time=datetime(2021, 8, 31, tzinfo=Utc()),
        name="Summer of 2021",
        year=2021
    )
)
```

### Create a Seasonal Field

In this example, we create a Seasonal Field, using the Season and Field objects
created in the preceding examples.

```python
from azure.identity import DefaultAzureCredential
from azure.agrifood.farming import FarmBeatsClient
from azure.agrifood.farming.models import SeasonalField

credential = DefaultAzureCredential()
client = FarmBeatsClient(endpoint="https://<my-account-name>.farmbeats.azure.net", credential=credential)

farmer_id = "farmer-1"
farm_id = "farm-1"
season_id = "season-summer-2021"

seasonal_field = client.seasonal_fields.create_or_update(
    farmer_id=farmer_id,
    seasonal_field_id="westlake-summer-2021",
    seasonal_field=SeasonalField(
        farm_id=farm_id,
        season_id=season_id
    )
)
```

### Create a Boundary

Creating a Boundary for the Seasonal Field created in the preceding example.

```python
from azure.identity import DefaultAzureCredential
from azure.agrifood.farming import FarmBeatsClient
from azure.agrifood.farming.models import Boundary, Polygon

credential = DefaultAzureCredential()
client = FarmBeatsClient(endpoint="https://<my-account-name>.farmbeats.azure.net", credential=credential)

farmer_id = "farmer-1"
seasonal_field_id = "westlake-summer-2021"

boundary = client.boundaries.create_or_update(
    farmer_id=farmer_id,
    boundary_id="westlake-boundary-1",
    boundary=Boundary(
        parent_id=seasonal_field_id,
        geometry=Polygon(
            coordinates=[
                [
                    [73.70457172393799, 20.545385304358106],
                    [73.70457172393799, 20.545385304358106],
                    [73.70448589324951, 20.542411534243367],
                    [73.70877742767334, 20.541688176010233],
                    [73.71023654937744, 20.545083911372505],
                    [73.70663166046143, 20.546992723579137],
                    [73.70457172393799, 20.545385304358106],
                ]
            ]
        )
    )
)
```

### Ingest Satellite Imagery

Triggering a Satellite Data Ingestion job for the boundary created above,
to ingest Leaf Area Index data for the month of January 2020.
This is a Long Running Operation (also called a 'Job'), and returns
a Poller object. Calling the `.result()` method on the poller object
waits for the operation to terminate, and returns the final status.

```python
from azure.identity import DefaultAzureCredential
from azure.agrifood.farming import FarmBeatsClient
from azure.agrifood.farming.models import SatelliteDataIngestionJob, SatelliteData

from isodate.tzinfo import Utc
from datetime import datetime

credential = DefaultAzureCredential()
client = FarmBeatsClient(endpoint="https://<my-account-name>.farmbeats.azure.net", credential=credential)

farmer_id = "farmer-1"
boundary_id = "westlake-boundary-1"

# Queue the job
satellite_job_poller = client.scenes.begin_create_satellite_data_ingestion_job(
    job_id="westlake-boundary-1-lai-jan2020",
    job=SatelliteDataIngestionJob(
        farmer_id=farmer_id,
        boundary_id=boundary_id,
        start_date_time=datetime(2020, 1, 1, tzinfo=Utc()),
        end_date_time=datetime(2020, 1, 31, tzinfo=Utc()),
        data=SatelliteData(
            image_names=[
                "LAI"
            ]
        )
    )
)

# Wait for the job to terminate
satellite_job = satellite_job_poller.result()
```

### Get Ingested Satellite Scenes

Querying for the scenes created by the job in the previous example.

```python
from azure.identity import DefaultAzureCredential
from azure.agrifood.farming import FarmBeatsClient

from datetime import datetime

credential = DefaultAzureCredential()
client = FarmBeatsClient(endpoint="https://<my-account-name>.farmbeats.azure.net", credential=credential)

farmer_id = "farmer-1"
boundary_id = "westlake-boundary-1"

scenes = client.scenes.list(
    farmer_id=farmer_id,
    boundary_id=boundary_id,
    start_date_time=datetime(2020, 1, 1, tzinfo=Utc()),
    end_date_time=datetime(2020, 1, 31, tzinfo=Utc()),
)

for scene in scenes:
    bands = [image_file.name for image_file in scene.image_files]
    bands_str = ", ".join(bands)
    print(f"Scene at {scene.scene_date_time} has the bands {bands_str}")
```

## Troubleshooting

### General

The FarmBeats client will raise exceptions defined in [Azure Core][azure_core] if you call `.raise_for_status()` on your responses.

### Logging

This library uses the standard
[logging][python_logging] library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.

Detailed DEBUG level logging, including request/response bodies and unredacted
headers, can be enabled on a client with the `logging_enable` keyword argument:

```python
import sys
import logging
from azure.identity import DefaultAzureCredential
from azure.agrifood.farming import FarmBeatsClient

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

endpoint = "https://<my-account-name>.farmbeats.azure.net"
credential = DefaultAzureCredential()

# This client will log detailed information about its HTTP sessions, at DEBUG level
client = FarmBeatsClient(endpoint=endpoint, credential=credential, logging_enable=True)
```

Similarly, `logging_enable` can enable detailed logging for a single call,
even when it isn't enabled for the client:

```python
client.crops.get(crop_id="crop_id", logging_enable=True)
```

## Next steps

### Additional documentation
For more extensive documentation on the FarmBeats, see the [FarmBeats documentation][product_docs] on docs.microsoft.com.

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->
[api_docs]: https://aka.ms/FarmBeatsAPIDocumentationPaaS
[authenticate_with_token]: https://docs.microsoft.com/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-an-authentication-token
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[azure_subscription]: https://azure.microsoft.com/free/
[change_log]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agrifood/azure-agrifood-farming/CHANGELOG.md
[cla]: https://cla.microsoft.com
[coc_contact]: mailto:opencode@microsoft.com
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential/
[farm_hierarchy]: https://aka.ms/FarmBeatsFarmHierarchyDocs
[farm_operations_docs]: https://aka.ms/FarmBeatsFarmOperationsDocumentation
[install_farmbeats]: https://aka.ms/FarmBeatsInstallDocumentationPaaS
[product_docs]: https://aka.ms/FarmBeatsProductDocumentationPaaS
[pip]: https://pypi.org/project/pip/
[pypi]: https://pypi.org/
[pypi-package]: https://pypi.org/project/azure-agrifood-farming/
[python]: https://www.python.org/downloads/
[python_logging]: https://docs.python.org/3.5/library/logging.html
[samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agrifood/azure-agrifood-farming/samples/
[scenes]: https://aka.ms/FarmBeatsSatellitePaaSDocumentation
[source_code]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agrifood/azure-agrifood-farming/
