# ==========================================
# Install azure-ai-language-questionanswering package with command
# ==========================================

# pip install azure-ai-language-questionanswering

# ==========================================
# Tasks Included
# ==========================================
# Create a project
# Update a project
# Deploy a project
# Getting Project data (Sources, QA pairs and synonyms)
# Get Answer
# Delete Project
# ==========================================
# Further reading
# General documentation: https://learn.microsoft.com/en-us/azure/cognitive-services/language-service/question-answering/overview
# Reference documentation: https://learn.microsoft.com/en-us/python/api/overview/azure/ai-language-questionanswering-readme?view=azure-python
# ==========================================

# Dependencies
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring import QuestionAnsweringAuthoringClient
from azure.ai.language.questionanswering import QuestionAnsweringClient
from azure.ai.language.questionanswering import models as qna


# Setting Resource Variables
endpoint = "<ENTER_LANGUAGE_ENDPOINT_HERE>"
key = "<ENTER_LANGUAGE_KEY_HERE>"
project_name = "<ENTER_PROJECT_NAME_HERE>"


# Defining clients
authoring_client = QuestionAnsweringAuthoringClient(endpoint, AzureKeyCredential(key))
inference_client = QuestionAnsweringClient(endpoint, AzureKeyCredential(key))


# Create Project
def create_project(client, project_name):
    project = client.create_project(
        project_name=project_name,
        options={
            "description": "This is the description for a test project",
            "language": "en",
            "multilingualResource": False,
            "settings": {
                "defaultAnswer": "no answer"
            }
        })

    print("Created project info:")
    print("\tName: {}".format(project["projectName"]))
    print("\tLanguage: {}".format(project["language"]))
    print("\tDescription: {}".format(project["description"]))


# Update Project
def update_project(client, project_name):
    # sources
    sources_poller = client.begin_update_sources(
        project_name=project_name,
        sources=[{
            "op": "add",
            "value": {
                "displayName": "MicrosoftFAQ",
                "source": "https://docs.microsoft.com/azure/cognitive-services/QnAMaker/troubleshooting",
                "sourceUri": "https://docs.microsoft.com/azure/cognitive-services/QnAMaker/troubleshooting",
                "sourceKind": "url",
                "contentStructureKind": "unstructured",
                "refresh": False
            }
        }]
    )
    sources = sources_poller.result() # wait until done
    for item in sources:
        print("Source name: {}".format(item.get("displayName", "N/A")))
        print("\tSource: {}".format(item["source"]))
        print("\tSource uri: {}".format(item.get("sourceUri", "N/A")))
        print("\tSource kind: {}".format(item["sourceKind"]))
        
    # qnas
    qna_poller = client.begin_update_qnas(
        project_name=project_name,
        qnas=[{
            "op": "add",
            "value": {
                "questions": [
                    "hello"
                ],
                "answer": "Hello, please select from the list of questions or enter a new question to continue.",
                "metadata": {
                    "Category": "Chitchat",
                    "Chitchat": "begin"
                },
                 "dialog": {
                     "isContextOnly": False,
                     "prompts": [
                         {
                             "displayOrder": 1,
                             "qnaId": 1,
                             "displayText": "Prompt 1"
                         }
                     ]
                 }
            }
        }]
    )
    qnas = qna_poller.result()
    for item in qnas:
        print("Question Answer Pairs: {}".format(item["id"]))
        print("\tQuestions:")
        for question in item["questions"]:
            print("\t\t{}".format(question))
        print("\tAnswer: {}".format(item["answer"]))
        
    # synonyms
    client.update_synonyms(
        project_name=project_name,
        synonyms={
            "value": [
                {
                    "alterations": [
                        "cqa",
                        "custom question answering"
                    ]
                },
                {
                    "alterations": [
                        "qa",
                        "question answer"
                    ]
                }
            ]
        }
    )
    print("Synonyms updated")


# Deploy Project
def deploy_project(client, project_name):
    deployment_poller = client.begin_deploy_project(
        project_name=project_name,
        deployment_name="production"
    )
    deployment = deployment_poller.result()
    print(f"Deployment successfully created under {deployment['deploymentName']}.")


# Get Project Data
def get_project_data(client, project_name):
    # Get QnAs
    qnas = client.list_qnas(
        project_name=project_name
    )
    print("Question Answer Pairs:")
    for item in qnas:
        print("ID: {}".format(item["id"]))
        print("\tQuestions:")
        for question in item["questions"]:
            print("\t\t{}".format(question))
        print("\tAnswer: {}".format(item["answer"]))
    
    #Get Sources
    sources = client.list_sources(
        project_name=project_name
    )
    print('')
    print("Sources")
    for item in sources:
        print("Source name: {}".format(item.get("displayName", "N/A")))
        print("\tSource: {}".format(item["source"]))
        print("\tSource uri: {}".format(item.get("sourceUri", "N/A")))
        print("\tSource kind: {}".format(item["sourceKind"]))
        
    # Get Synonyms
    synonyms = client.list_synonyms(
        project_name=project_name
    )
    print('')
    print("Synonyms:")
    for item in synonyms:
        print("\tAlterations:")
        for alt in item["alterations"]:
            print("\t\t{}".format(alt))


# Get Answer
def get_answer(client, project_name):
    question="How do I manage my knowledgebase?"
    output = client.get_answers(
        question=question,
        top=3,
        confidence_threshold=0.2,
        include_unstructured_sources=True,
        short_answer_options=qna.ShortAnswerOptions(
            confidence_threshold=0.2,
            top=1
        ),
        project_name=project_name,
        deployment_name="test"
    )
    best_candidate = output.answers[0]
    print("Q: {}".format(question))
    print("A: {}".format(best_candidate.answer))
    print("Score: {}".format(best_candidate.confidence))


# Delete Project
def delete_project(client, project_name):
    delete_poller = client.begin_delete_project(
        project_name=project_name
    )
    delete_poller.result()
    print(f"Delete successful.")


# Operations
create_project(authoring_client, project_name)
update_project(authoring_client, project_name)
deploy_project(authoring_client, project_name)
get_project_data(authoring_client, project_name)
get_answer(inference_client, project_name)
delete_project(authoring_client, project_name)

