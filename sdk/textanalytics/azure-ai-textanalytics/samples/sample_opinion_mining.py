
documents = ["It has a sleek premium aluminum design that makes it beautiful to look at."]

result = text_analytics_client.analyze_sentiment(documents)
doc_result = [doc for doc in result if not doc.is_error][0]


for sentence in doc_result:
    for aspect in sentence.aspects:
        print(aspect.text)  # 'design'
        print(aspect.sentiment)  # 'positive'
        print(aspect.confidence_scores.positive)  # 1.0
        print(aspect.confidence_scores.negative)  # 0.0
        print(aspect.offset)  # 32
        print(aspect.length)  # 6

        for opinion in aspect.opinions:
            # there should be two opinions. Will include both values in comments
            print(opinion.text)  # 'sleek' & 'premium'
            print(opinion.sentiment)  # 'positive' & 'positive'
            print(opinion.confidence_scores.positive)  # 1.0 & 1.0
            print(opinion.confidence_scores.negative)  # 0.0 & 0.0
            print(opinion.offset)  # 9 & 15
            print(opinion.length)  # 5 & 7
            print(opinion.is_negated)  # False & False
