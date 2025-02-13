import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


def fetch_stackoverflow_data(tags, from_date, to_date):
    url = "https://api.stackexchange.com/2.3/questions"
    params = {
        "order": "desc",
        "sort": "creation",
        "tagged": ";".join(tags),
        "site": "stackoverflow",
        "pagesize": 100,
        "fromdate": int(from_date.timestamp()),
        "todate": int(to_date.timestamp()),
    }
    questions = []
    has_more = True
    while has_more:
        response = requests.get(url, params=params)
        data = response.json()
        questions.extend(data["items"])
        has_more = data["has_more"]
        if has_more:
            params["page"] = params.get("page", 1) + 1
    return questions


def process_data(questions):
    dates = [datetime.fromtimestamp(q["creation_date"]) for q in questions]
    df = pd.DataFrame(dates, columns=["date"])
    df["month"] = df["date"].dt.to_period("M")
    return df.groupby("month").size()


def plot_data(data, tags):
    plt.figure(figsize=(12, 6))
    plt.plot(data.index.astype(str), data, marker="o", label="Monthly Questions")

    # Calculate and plot the rolling mean (trend)
    rolling_mean = data.rolling(window=3, center=True).mean()
    plt.plot(data.index.astype(str), rolling_mean, color="red", linestyle="--", label="3-Month Rolling Mean")

    plt.title(f"Number of Questions per Month Tagged '{', '.join(tags)}' on Stack Overflow")
    plt.xlabel("Month")
    plt.ylabel("Number of Questions")
    plt.legend()
    plt.grid(True)

    # Customize x-axis to show fewer date timestamps
    plt.xticks(ticks=range(0, len(data), 3), labels=data.index[::3].astype(str), rotation=45)

    plt.show()


if __name__ == "__main__":
    tags = ["azure", "python"]
    to_date = datetime.now()
    from_date = to_date - timedelta(days=3 * 365)

    print(f"Fetching data for tags: {', '.join(tags)}")
    questions = fetch_stackoverflow_data(tags, from_date, to_date)
    data = process_data(questions)
    plot_data(data, tags)
