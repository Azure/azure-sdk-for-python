

import logging
from datetime import timedelta
import os
from pathlib import Path

from flask import (
    Blueprint,
    Flask,
    jsonify,
    request,
    send_from_directory,
)

from openai_messages_token_helper import build_messages, get_token_limit


from azure.cloudmachine.ext.flask import CloudMachine
from azure.cloudmachine import resources, StorageFile, DeletedFile
from azure.cloudmachine.provisioning import CloudMachineDeployment
from azure.cloudmachine.events import FILE_UPLOADED, FILE_DELETED

from error import error_response

bp = Blueprint("routes", __name__, static_folder="static")


openai = resources.get('openai')['shared']
openai.set('embeddings_model', 'text-embedding-ada-002')
openai.set('embeddings_deployment', 'text-embedding-ada-002')
openai.set('chat_model', 'gpt-35-turbo')
openai.set('chat_deployment', 'gpt-35-turbo')


deployment = CloudMachineDeployment(
    name="searchopenaidemo",
    host="local",
    location="westus2",
    search=True,
    documentai=True
)

cm = CloudMachine(
    deployment=deployment,
    openai=openai
)


system_prompt_chat = """Assistant helps the user answer questions from the list of source documents. Be brief in your answers.
Answer ONLY with the facts listed in the list of sources below. If there isn't enough information below, say you don't know. Do not generate answers that don't use the sources below. If asking a clarifying question to the user would help, ask the question.
If the question is not in English, answer in the language used in the question.
Each source has a name followed by colon and the actual information, always include the source name for each fact you use in the response. Use square brackets to reference the source, for example [info1.txt]. Don't combine sources, list each source separately, for example [info1.txt][info2.pdf].
"""
system_prompt_ask = """You are an intelligent assistant helping Contoso Inc employees with their healthcare plan questions and employee handbook questions. 
Use 'you' to refer to the individual asking the questions even if they ask with 'I'. 
Answer the following question using only the data provided in the sources below. 
Each source has a name followed by colon and the actual information, always include the source name for each fact you use in the response. 
If you cannot answer using the sources below, say you don't know."
"""

@FILE_UPLOADED.connect
def uploaded(cm: CloudMachine, event: StorageFile[None]):
    print("Uploaded", event)
    cm.document_index.add_file(
        file=cm.storage.download(event.filename),
        url=cm.storage.get_url(file=event, expiry=timedelta(days=1))
    )
    print("Finished indexing", event.filename)


@FILE_DELETED.connect
def deleted(cm: CloudMachine, event: DeletedFile):
    print("Deleted", event)
    cm.document_index.remove_file(file=event.filename)
    print("Removed from index", event.filename)


@bp.route("/")
def index():
    return bp.send_static_file("index.html")


@bp.route("/favicon.ico")
def favicon():
    return bp.send_static_file("favicon.ico")


@bp.route("/assets/<path:path>")
def assets(path):
    return send_from_directory(Path(__file__).resolve().parent / "static" / "assets", path)


@bp.route("/ask", methods=["POST"])
def ask():
    if not request.is_json:
        return jsonify({"error": "request must be json"}), 415
    request_json = request.get_json()
    messages = request_json["messages"]

    try:
        openai_client, settings = cm.get_client("openai:chat", with_settings=True)
        model = settings.get('chat_model')
        user_query = messages[-1]["content"]

        documents = cm.document_index.search(
            query=user_query,
        )
        source_content = cm.document_index.get_sources(documents)
        response_token_limit = 1024
        messages = build_messages(
            model=model,
            system_prompt=system_prompt_ask,
            past_messages=messages[:-1],
            new_user_content=user_query + "\n\nSources:\n" + "\n".join(source_content),
            max_tokens=get_token_limit(model) - response_token_limit,
        )

        completion = openai_client.completions.create(
                model=model,
                messages=messages,
                temperature=0.3,
                max_tokens=response_token_limit,
                n=1
            )
        content = completion.choices[0].message.content
        role = completion.choices[0].message.role
        result = {
            "message": {"content": content, "role": role},
            "session_state": request_json["session_state"],
            "context": {
                "data_points": {"text": source_content},
            }
        }
        return jsonify(result)
    except Exception as error:
        return error_response(error, "/ask")


@bp.post("/upload")
def upload():
    request_files = request.files
    if "file" not in request_files:
        # If no files were included in the request, return an error response
        return jsonify({"message": "No file part in the request", "status": "failed"}), 400

    cm.storage.upload(
        request_files.getlist("file")[0],
        overwrite=True,
    )
    return jsonify({"message": "File uploaded successfully"}), 200

@bp.post("/delete_uploaded")
def delete_uploaded():
    request_json = request.get_json()
    filename = request_json.get("filename")
    cm.storage.delete(filename)
    return jsonify({"message": f"File {filename} deleted successfully"}), 200


@bp.get("/list_uploaded")
def list_uploaded():
    files = [blob.filename.split("/", 1)[-1] for blob in cm.storage.list(minimal=True)]
    return jsonify(files), 200


def create_app():
    app = Flask(__name__)
    cm.init_app(app)
    app.register_blueprint(bp)

    logging.basicConfig(level=logging.WARNING)
    default_level = "INFO"
    app.logger.setLevel(os.getenv("APP_LOG_LEVEL", default_level))

    return app
