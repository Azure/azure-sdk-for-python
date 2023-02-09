from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import (
       TextAnalyticsClient,
       RecognizeEntitiesAction,
       RecognizeLinkedEntitiesAction,
       RecognizePiiEntitiesAction,
       ExtractKeyPhrasesAction,
       AnalyzeSentimentAction,
       RecognizeCustomEntitiesAction,
       SingleLabelClassifyAction,
       MultiLabelClassifyAction,
       AnalyzeHealthcareEntitiesAction,
       ExtractSummaryAction,
       AbstractSummaryAction
)
import os

endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
key = os.environ["AZURE_LANGUAGE_KEY"]


text_analytics_client = TextAnalyticsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key),
)

documents = [
    'We went to Contoso Steakhouse located at midtown NYC last week for a dinner party, and we adore the spot! '
    'They provide marvelous food and they have a great menu. The chief cook happens to be the owner (I think his name is John Doe) '
    'and he is super nice, coming out of the kitchen and greeted us all.'
    ,

    'We enjoyed very much dining in the place! '
    'The Sirloin steak I ordered was tender and juicy, and the place was impeccably clean. You can even pre-order from their '
    'online menu at www.contososteakhouse.com, call 312-555-0176 or send email to order@contososteakhouse.com! '
    'The only complaint I have is the food didn\'t come fast enough. Overall I highly recommend it!'
]

poller = text_analytics_client.begin_analyze_actions(
    documents,
    display_name="Multiple Analysis",
    actions=[
        RecognizeEntitiesAction(),
        RecognizeLinkedEntitiesAction(),
        RecognizePiiEntitiesAction(),
        ExtractKeyPhrasesAction(),
        AnalyzeSentimentAction(),
        RecognizeCustomEntitiesAction('customner', 'customner'),
        SingleLabelClassifyAction('singleclassify', 'singleclassify'),
        MultiLabelClassifyAction('multiclassify', 'multiclassify'),#project_name, deployment_name),
        AnalyzeHealthcareEntitiesAction(),
        ExtractSummaryAction(),
        AbstractSummaryAction(),
    ],
)

document_results = poller.result()
for doc, action_results in zip(documents, document_results):
    print(f"\nDocument text: {doc}")
    for result in action_results:
        print(result.kind)
        if result.kind == "EntityRecognition":
            print("...Results of Recognize Entities Action:")
            for entity in result.entities:
                print(f"......Entity: {entity.text}")
                print(f".........Category: {entity.category}")
                print(f".........Confidence Score: {entity.confidence_score}")
                print(f".........Offset: {entity.offset}")

        elif result.kind == "EntityLinking":
            print("...Results of Recognize Linked Entities action:")
            for linked_entity in result.entities:
                print(f"......Entity name: {linked_entity.name}")
                print(f".........Data source: {linked_entity.data_source}")
                print(f".........Data source language: {linked_entity.language}")
                print(
                    f".........Data source entity ID: {linked_entity.data_source_entity_id}"
                )
                print(f".........Data source URL: {linked_entity.url}")
                print(".........Document matches:")
                for match in linked_entity.matches:
                    print(f"............Match text: {match.text}")
                    print(f"............Confidence Score: {match.confidence_score}")
                    print(f"............Offset: {match.offset}")
                    print(f"............Length: {match.length}")

        elif result.kind == "PiiEntityRecognition":
            print("...Results of Recognize PII Entities action:")
            for entity in result.entities:
                print(f"......Entity: {entity.text}")
                print(f".........Category: {entity.category}")
                print(f".........Confidence Score: {entity.confidence_score}")

        elif result.kind == "KeyPhraseExtraction":
            print("...Results of Extract Key Phrases action:")
            print(f"......Key Phrases: {result.key_phrases}")

        elif result.kind == "SentimentAnalysis":
            print("...Results of Analyze Sentiment action:")
            print(f"......Overall sentiment: {result.sentiment}")
            print(
                f"......Scores: positive={result.confidence_scores.positive}; \
                neutral={result.confidence_scores.neutral}; \
                negative={result.confidence_scores.negative} \n"
            )
        
        elif result.kind == "CustomEntityRecognition":
            print("...Results of Recognize Custom Entities Action:")
            for entity in result.entities:
                print(f"......Entity: {entity.text}")
                print(f".........Category: {entity.category}")
                print(f".........Confidence Score: {entity.confidence_score}")
                print(f".........Offset: {entity.offset}")

        elif result.kind == "CustomDocumentClassification":
            print("...Results of Classify Multi/Single Label Action:")
            for classification in result.classifications:
                print(f"......Category: {classification.category}")
                print(f"......Confidence Score: {classification.confidence_score}")       

        elif result.kind == "Healthcare":
            print("...Results of Analyze Healthcare Entities Action:")
            for entity in result.entities:
                print(f"......Entity: {entity.text}")
                print(f".........Category: {entity.category}")
                print(f".........Offset: {entity.offset}")
                print(f".........Length: {entity.length}")


        elif result.kind == "ExtractiveSummarization":
            print("...Results of Extract Summary Action:")
            for sentence in result.sentences:
                print(f"......Sentence: {sentence.text}")
                print(f".........Rank Score: {sentence.rank_score}")
                print(f".........Offset: {sentence.offset}")
                print(f".........Length: {sentence.length}")

        # The supported regions are North Europe, East US, UK South.
        elif result.kind == "AbstractiveSummarization":
            print("...Results of Abstract Summary Action:")
            for summary in result.summaries:
                print("......Summary: {0}".format(summary.text.replace('\n', ' ')))
                for context in summary.contexts:
                    print(f".........Context Offset: {context.offset}")
                    print(f".........Context Length: {context.length}")


        elif result.is_error is True:
            print(
                f"...Is an error with code '{result.code}' and message '{result.message}'"
            )

    print("------------------------------------------")
