
documents = ["The food is good and not yummy"]

result = text_analytics_client.analyze_sentiment(documents)
doc_result = [doc for doc in result if not doc.is_error][0]


for sentence in doc_result:
    for aspect in sentence.aspects:
        print(aspect.text)  # 'food'
        print(aspect.sentiment)  # 'mixed'
        print(aspect.confidence_scores.positive)  # 0.52
        print(aspect.confidence_scores.negative)  # 0.48
        print(aspect.offset)  # 4
        print(aspect.length)  # 4

        for opinion in aspect.opinions:
            # there should be two opinions. Will include both values in comments
            print(opinion.text)  # 'good' & 'yummy'
            print(opinion.sentiment)  # 'positive' & 'negative'
            print(opinion.confidence_scores.positive)  # 1.0 & 0.03
            print(opinion.confidence_scores.negative)  # 0.0 & 0.97
            print(opinion.offset)  # 12 & 25
            print(opinion.length)  # 4 & 5
            print(opinion.is_negated)  # False & True
