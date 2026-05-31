# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Generates supervised fine-tuning data from a Markdown reference document
    uploaded as an Azure OpenAI File. The sample:

      1. Uploads a short reference document via the Azure OpenAI Files API
         (`purpose=user_data`) so it can be referenced by file id.
      2. Creates a `DataGenerationJob` (scenario=SUPERVISED_FINETUNING,
         type=simple_qna) that synthesizes short-answer and long-answer
         question / answer pairs from the file content and emits them as
         training and validation JSONL files.
      3. Polls the job to completion and prints every generated file output.
      4. Cleans up the generated fine-tuning files, the Azure OpenAI input file, and the data generation job.

    `simple_qna` REQUIRES `model_options` — the service uses the configured LLM
    to synthesize the QnA pairs. Setting `train_split` triggers a split of
    the generated samples into two Azure OpenAI output files.

USAGE:
    python sample_dataset_generation_job_simpleqna_for_finetuning.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" azure-identity openai python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found
       in the overview page of your Microsoft Foundry project.
    2) FOUNDRY_MODEL_NAME - Required. The name of an Azure OpenAI model
       deployment used to synthesize the QnA samples. For `simple_qna` fine-tuning,
       the deployment must support the chat completions API (e.g. `gpt-4o`, `gpt-4.1`).
    3) DATASET_NAME - Optional. Name to assign to the generated output files
       (used as the file name prefix). Defaults to `simpleqna-finetuning-sample`.
       The service caps the rendered output name at 50 characters, so keep
       custom values short — the sample appends a unique run id suffix.
    4) POLL_INTERVAL_SECONDS - Optional. Number of seconds to sleep between status
       polls for the data generation job. Defaults to 10.
"""

import io
import os
import time
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    DataGenerationJob,
    DataGenerationJobInputs,
    DataGenerationJobOutputOptions,
    DataGenerationJobScenario,
    DataGenerationModelOptions,
    FileDataGenerationJobOutput,
    FileDataGenerationJobSource,
    JobStatus,
    SimpleQnADataGenerationJobOptions,
    SimpleQnAFineTuningQuestionType,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_name = os.environ["FOUNDRY_MODEL_NAME"]
dataset_name = os.environ.get("DATASET_NAME", "simpleqna-finetuning-sample")
poll_interval_seconds = int(os.environ.get("POLL_INTERVAL_SECONDS", "10"))

# Unique per-run output name so repeated runs do not collide.
# Output names are capped at 50 characters by the service.
run_id = f"{datetime.now(tz=timezone.utc).strftime('%y%m%d%H%M%S')}-{uuid.uuid4().hex[:4]}"
output_name = f"{dataset_name}-{run_id}"
if len(output_name) > 50:
    raise ValueError(
        f"Output name `{output_name}` exceeds the 50-character service limit. "
        f"Lower DATASET_NAME (currently `{dataset_name}`) so that `<DATASET_NAME>-<run id>` fits within 50 characters."
    )

# Reference document the sample uploads as an Azure OpenAI file. SUPERVISED_FINETUNING
# QnA generation requires a substantially richer corpus than the eval scenario does;
# a 1-2 KB summary is not enough and the service will reject it with
# "File content lacks sufficient context to generate quality questions." Keep this
# block at roughly 8-12 KB of varied prose so the service has enough material to
# synthesize diverse question/answer pairs.
SEED_REFERENCE_DOCUMENT = """# Widgets, Gizmos, and Sprockets: Complete Product and Operations Reference

## 1. Product Catalog

### 1.1 Widget (model WDG-100)
The Widget is a structural carbon-fiber component manufactured at Factory 7 in Acme. It is
finished in matte blue (Pantone 2935 C) using a UV-stable powder coating. Each unit measures
120 mm x 40 mm x 18 mm and weighs 250 g (+/- 5 g). Widgets are rated for continuous service
up to 80 degrees Celsius and a transient peak of 95 degrees Celsius for up to 60 seconds.
Widgets ship in packs of 4, packaged in recyclable cardboard with biodegradable foam inserts.
The serial number is laser-etched on the underside in the format WDG-100-YYWW-NNNNN, where
YY is the two-digit year, WW is the ISO week, and NNNNN is the per-week sequence number.

Compatible mounting hardware: M5 stainless steel bolts, torqued to 6.0 Nm. Substituting
non-stainless bolts voids the corrosion portion of the warranty.

### 1.2 Gizmo (model GZM-200)
The Gizmo is a precision carbon-fiber assembly manufactured at Factory 12 in Bedrock. It is
finished in gloss red (Pantone 186 C). Each Gizmo measures 220 mm x 110 mm x 60 mm and
weighs 1.2 kg (+/- 20 g). Gizmos are sold individually and are rated to 80 degrees Celsius.
They include an integrated thermal cutoff that disables the unit at 88 degrees Celsius and
re-enables it after a five minute cool-down. The serial number is engraved on the side and
follows the format GZM-200-YYWW-NNNNN.

Compatible mounting hardware: M8 stainless steel bolts, torqued to 18 Nm. Gizmos should be
installed on a flat surface with no more than 0.5 mm of warp across the 220 mm dimension.

### 1.3 Sprocket (model SPR-300)
The Sprocket is a stainless-steel rotating component manufactured at Factory 3 in Acme.
It is finished in anodised green and weighs 500 g. The Sprocket is rated for continuous
service up to 200 degrees Celsius. The teeth count is 24, the pitch diameter is 60 mm,
and the bore is 12 mm with a standard 4 mm keyway. Sprockets ship individually with a
laser-etched serial number on the hub in the format SPR-300-YYWW-NNNNN.

Compatible mounting hardware: M12 stainless steel set screws, torqued to 22 Nm.

### 1.4 Compatibility matrix
* Widget + Gizmo: fully compatible, no adapter required.
* Widget + Sprocket: requires the WDG-SPR adapter plate (part WDG-SPR-A01).
* Gizmo + Sprocket: requires the GZM-SPR adapter plate (part GZM-SPR-A02) and a 4 mm shim.
* Widget + Gizmo + Sprocket (three-way stack): requires both adapter plates and the
  triple-stack bracket WGS-T01. Torque all bolts to spec in the sequence Widget,
  Gizmo, Sprocket.

## 2. Manufacturing and Operations

### 2.1 Factory schedule
All three factories operate weekdays from 0700 to 1900 local time. Factories are closed
on national public holidays except for the annual maintenance run on December 27, when
each factory performs cleaning, lubrication, and recalibration of CNC equipment and
finishing lines. The maintenance run runs from 0600 to 1400 local time and does not
produce shippable inventory.

### 2.2 Quality control
Every factory is ISO 9001:2015 certified and is audited annually by an independent
third party. Quality control samples every 100th unit for visual and dimensional
inspection. Every 5000th unit undergoes full destructive testing including tensile,
compressive, and thermal cycling. Destructive test results are archived for seven
years and are available to enterprise customers on request.

### 2.3 Lot traceability
The first four characters of every serial number identify the model, the next four
characters identify the ISO year and week, and the remaining five characters identify
the per-week sequence number. Given any serial number, customer support can identify
the production line, the shift, the operator, and the raw material lot that produced
the unit. Lot traceability records are retained for the life of the product plus three
years.

### 2.4 Environmental
All three factories are powered by a mix of on-site solar and grid-tied wind generation.
Total Scope 1 and Scope 2 emissions for FY2025 were 12,400 tonnes CO2e, a 14 percent
reduction from FY2024. Packaging is fully recyclable; the cardboard boxes are made from
80 percent post-consumer recycled fibre and the biodegradable foam is corn-starch based.

## 3. Pricing and Ordering

### 3.1 Standard list prices
* Widget 4-pack (WDG-100-PK4): USD 24.99
* Gizmo single (GZM-200): USD 49.99
* Sprocket single (SPR-300): USD 14.99
* WDG-SPR adapter plate: USD 6.50
* GZM-SPR adapter plate: USD 7.50
* Triple-stack bracket WGS-T01: USD 18.00

### 3.2 Shipping
Free standard shipping is provided on orders over USD 75 within the United States and
Canada. International orders incur shipping based on weight and destination, computed
at checkout. Standard transit time within North America is 3 to 5 business days. Express
overnight shipping is available for an additional USD 18 per shipment.

### 3.3 Bulk orders
Bulk orders of 50 or more units of any single product receive a 12 percent discount
on the list price plus a 90 day return window. Bulk orders of 250 or more units
receive an 18 percent discount and the option of a dedicated account manager. Contact
sales@example.com for bulk orders.

### 3.4 Payment terms
Standard payment is due at checkout via credit card or PayPal. Enterprise customers
with an approved purchase order may pay net 30 days from invoice date. Late payments
incur a 1.5 percent monthly service charge.

## 4. Warranty and Returns

### 4.1 Standard warranty
All products carry a two year limited warranty against defects in materials and
workmanship from the date of purchase. The warranty does not cover damage from
incorrect installation, exposure beyond the rated temperature range, modification,
or normal wear. Warranty service is provided by repair, replacement, or refund at
the manufacturer's discretion.

### 4.2 Filing a warranty claim
Warranty claims are filed by emailing support@example.com with the product serial
number, a description of the issue, and photographs of the failure mode. Acme will
respond within one business day with either a Return Merchandise Authorisation (RMA)
number or a request for additional information. RMAs are valid for 30 days and must
be referenced on the outside of any returned package.

### 4.3 Returns
Unopened products can be returned within 30 days of receipt for a full refund.
Opened products are eligible for repair only, except where required by local law.
Bulk orders (50+ units) are eligible for return within 90 days under the same
unopened/opened rules. Custom-finished products are non-returnable.

### 4.4 Repair turnaround
The target turnaround for in-warranty repair is 10 business days from receipt at the
service centre. Out-of-warranty repair is offered at a fixed rate of USD 35 per
Widget, USD 60 per Gizmo, or USD 20 per Sprocket, plus return shipping.

## 5. Installation and Use

### 5.1 Pre-installation checks
Before installing any product, inspect for transit damage. If the box shows signs of
crushing or moisture, photograph the damage before opening and report it to
support@example.com within 48 hours. Confirm that the serial number on the unit
matches the packing slip.

### 5.2 Widget installation
Mount Widgets on a flat surface with M5 stainless steel bolts torqued to 6.0 Nm in
a star pattern. Apply a thin film of anti-seize compound to the bolt threads. Allow
the assembly to cure for 30 minutes before applying load.

### 5.3 Gizmo installation
Mount Gizmos on a flat surface with M8 stainless steel bolts torqued to 18 Nm.
Do not exceed 22 Nm; over-torquing can crack the carbon-fiber housing. The thermal
cutoff cable must be routed away from heat sources and secured with the supplied
P-clips at intervals of no more than 200 mm.

### 5.4 Sprocket installation
Press the Sprocket onto a 12 mm shaft using an arbor press. Hand pressure or
percussive installation will damage the bore tolerance. Once seated, install the
M12 set screw in the keyway and torque to 22 Nm.

### 5.5 Periodic maintenance
Inspect mounting hardware every 6 months. Re-torque to spec if any fastener has
loosened. Replace any fastener that shows corrosion or thread damage. Clean exterior
surfaces with isopropyl alcohol and a microfiber cloth; do not use abrasive cleaners.

## 6. Customer Support

### 6.1 Contact channels
* Email: support@example.com (response within one business day)
* Priority email: priority@example.com (response within four hours for enterprise
  customers with a current support agreement)
* Phone: 1-800-555-0100, Monday to Friday, 0800 to 1800 Eastern Time
* Self-service portal: https://support.example.com

### 6.2 Service level agreements
The standard SLA is a one business day first response for general inquiries and a
four hour first response for priority inquiries. Critical production-down issues for
enterprise customers receive a one hour first response and a continuous-effort
resolution target until the issue is resolved.

### 6.3 Replacement parts
Replacement parts including bolts, adapter plates, P-clips, and thermal cutoff
cables can be ordered directly from the support portal using the original order
number. Common parts ship the same business day if ordered before 1500 Eastern Time.

## 7. Frequently Asked Questions

Q. What is the maximum operating temperature of a Widget?
A. 80 degrees Celsius continuous, with a transient peak of 95 degrees Celsius for
up to 60 seconds.

Q. Can I install a Gizmo with non-stainless bolts?
A. No. Using non-stainless bolts voids the corrosion portion of the warranty.

Q. Does the Sprocket fit a 12 mm shaft?
A. Yes. The Sprocket bore is 12 mm with a standard 4 mm keyway.

Q. What is the lead time for bulk orders of 250 units?
A. Standard lead time is 10 to 15 business days, plus shipping.

Q. How do I know when my Gizmo's thermal cutoff has tripped?
A. The unit will go silent and the status LED will blink red twice per second.
After five minutes the unit will automatically re-enable and resume normal operation.

Q. Where do I find the serial number?
A. Widget: laser-etched on the underside. Gizmo: engraved on the side. Sprocket:
laser-etched on the hub.

Q. Are your products RoHS compliant?
A. Yes. All three products comply with EU RoHS 2 (Directive 2011/65/EU) and RoHS 3
(Directive 2015/863).

Q. Do you offer custom colours?
A. Custom finishes are available for orders of 500 or more units. Contact
sales@example.com for a custom-finish quote. Custom-finished products are
non-returnable.

Q. What torque should I use for the M8 bolts on a Gizmo?
A. 18 Nm. Do not exceed 22 Nm.

Q. How long is the warranty?
A. Two years from date of purchase against defects in materials and workmanship.
"""

TERMINAL_STATUSES = {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED}

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):

    # ------------------------------------------------------------------
    # 1. Upload the seed reference document as an Azure OpenAI file.
    # ------------------------------------------------------------------
    seed_filename = f"widgets-gizmos-seed-{run_id}.md"
    print(f"Upload the seed reference document as Azure OpenAI file `{seed_filename}`.")
    seed_file = openai_client.files.create(
        file=(seed_filename, io.BytesIO(SEED_REFERENCE_DOCUMENT.encode("utf-8"))),
        purpose="user_data",
    )
    print(f"Uploaded Azure OpenAI file (id: {seed_file.id}).")

    # Wait for the file to finish processing — the data generation service
    # rejects references to files that are not yet in the `processed` state.
    print("Wait for the Azure OpenAI file to be processed.", end="", flush=True)
    while seed_file.status not in ("processed", "error"):
        time.sleep(2)
        seed_file = openai_client.files.retrieve(file_id=seed_file.id)
        print(".", end="", flush=True)
    print()
    if seed_file.status != "processed":
        raise RuntimeError(f"Azure OpenAI file `{seed_file.id}` failed to process: status=`{seed_file.status}`.")

    # ------------------------------------------------------------------
    # 2. Submit a fine-tuning data generation job that consumes the file.
    # ------------------------------------------------------------------
    print("Create a fine-tuning data generation job from the Azure OpenAI file.")
    job = DataGenerationJob(
        inputs=DataGenerationJobInputs(
            name=f"simpleqna-finetuning-{run_id}",
            scenario=DataGenerationJobScenario.SUPERVISED_FINETUNING,
            sources=[
                FileDataGenerationJobSource(
                    description="Widgets & Gizmos product / operations reference (Azure OpenAI file).",
                    id=seed_file.id,
                ),
            ],
            options=SimpleQnADataGenerationJobOptions(
                # Service requires max_samples to be between 15 and 1000.
                max_samples=15,
                # `simple_qna` REQUIRES model_options.
                model_options=DataGenerationModelOptions(model=model_name),
                # Split generated samples 80% training / 20% validation.
                train_split=0.8,
                # Ask for both short-answer and long-answer questions.
                question_types=[
                    SimpleQnAFineTuningQuestionType.SHORT_ANSWER,
                    SimpleQnAFineTuningQuestionType.LONG_ANSWER,
                ],
            ),
            output_options=DataGenerationJobOutputOptions(name=output_name),
        ),
    )
    job = project_client.beta.datasets.create_generation_job(job=job)
    print(f"Created data generation job `{job.id}` (status: `{job.status}`).")

    print(f"Poll job `{job.id}` until it reaches a terminal state.", end="", flush=True)
    while True:
        job = project_client.beta.datasets.get_generation_job(job_id=job.id)
        if job.status in TERMINAL_STATUSES:
            break
        time.sleep(poll_interval_seconds)
        print(".", end="", flush=True)
    print()
    print(f"Final job status: `{job.status}`.")

    if job.status != JobStatus.SUCCEEDED:
        message = job.error.message if job.error is not None else "<no error message>"
        raise RuntimeError(f"Job `{job.id}` ended with status `{job.status}`: {message}")

    # ------------------------------------------------------------------
    # 3. Inspect the generated fine-tuning file outputs.
    # ------------------------------------------------------------------
    # `train_split=0.8` produces two Azure OpenAI files: a training partition
    # and a validation partition. Both are emitted as FileDataGenerationJobOutput
    # entries in `job.result.outputs`.
    file_outputs = [
        output
        for output in ((job.result.outputs if job.result is not None else None) or [])
        if isinstance(output, FileDataGenerationJobOutput)
    ]
    if not file_outputs:
        raise RuntimeError(f"Job `{job.id}` did not produce any file outputs.")

    print(f"Generated {len(file_outputs)} fine-tuning file(s):")
    for output in file_outputs:
        if not output.id:
            raise RuntimeError(f"Job `{job.id}` returned a file output without an id.")
        # Resolve the Azure OpenAI file to surface its real filename and size.
        file_info = openai_client.files.retrieve(file_id=output.id)
        print(f"  - filename=`{file_info.filename}` id=`{output.id}` bytes={file_info.bytes}")
    if job.result is not None and job.result.generated_samples is not None:
        print(f"Generated samples: {job.result.generated_samples}")

    # ------------------------------------------------------------------
    # 4. Clean up.
    # ------------------------------------------------------------------
    for output in file_outputs:
        print(f"Delete the generated Azure OpenAI file `{output.id}`.")
        openai_client.files.delete(file_id=output.id)

    print(f"Delete the Azure OpenAI input file `{seed_file.id}`.")
    openai_client.files.delete(file_id=seed_file.id)

    print(f"Delete the data generation job `{job.id}`.")
    project_client.beta.datasets.delete_generation_job(job_id=job.id)
