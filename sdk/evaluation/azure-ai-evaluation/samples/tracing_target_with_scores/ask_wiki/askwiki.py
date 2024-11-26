# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=ANN201,ANN001,RET505
import json
import os
import pathlib
import random
import time
import uuid
from functools import partial

import jinja2
import requests
import bs4
import re
from concurrent.futures import ThreadPoolExecutor
from openai import AzureOpenAI
from typing import List, Tuple, TypedDict
from opentelemetry import trace
from gen_ai_trace import gen_ai_trace

from opentelemetry.trace import get_tracer
tracer = get_tracer("AskWiki")

# Create a session for making HTTP requests
session = requests.Session()

# Set up Jinja2 for templating
templateLoader = jinja2.FileSystemLoader(pathlib.Path(__file__).parent.resolve())
templateEnv = jinja2.Environment(loader=templateLoader)
system_message_template = templateEnv.get_template("system-message.jinja2")


# Function to decode a string
def decode_str(string: str) -> str:
    return string.encode().decode("unicode-escape").encode("latin1").decode("utf-8")


# Function to remove nested parentheses from a string
def remove_nested_parentheses(string: str) -> str:
    pattern = r"\([^()]+\)"
    while re.search(pattern, string):
        string = re.sub(pattern, "", string)
    return string


# Function to get sentences from a page
def get_page_sentence(page: str, count: int = 10) -> str:
    # find all paragraphs
    paragraphs = page.split("\n")
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    # find all sentence
    sentences = []
    for p in paragraphs:
        sentences += p.split(". ")
    sentences = [s.strip() + "." for s in sentences if s.strip()]
    # get first `count` number of sentences
    return " ".join(sentences[:count])


# Function to fetch text content from a URL
def fetch_text_content_from_url(url: str, count: int = 10) -> Tuple[str, str]:
    # Send a request to the URL
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35"
        }
        delay = random.uniform(0, 0.5)
        time.sleep(delay)
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            # Parse the HTML content using BeautifulSoup
            soup = bs4.BeautifulSoup(response.text, "html.parser")
            page_content = [p_ul.get_text().strip() for p_ul in soup.find_all("p") + soup.find_all("ul")]
            page = ""
            for content in page_content:
                if len(content.split(" ")) > 2:
                    page += decode_str(content)
                if not content.endswith("\n"):
                    page += "\n"
            text = get_page_sentence(page, count=count)
            return (url, text)
        msg = (
            f"Get url failed with status code {response.status_code}.\nURL: {url}\nResponse: " f"{response.text[:100]}"
        )
        print(msg)
        return (url, "No available content")

    except Exception as e:
        print("Get url failed with error: {}".format(e))
        return (url, "No available content")


@tracer.start_as_current_span(name="search_result_from_url")
# Function to get search results from a list of URLs
def search_result_from_url(url_list: List[str], count: int = 10) -> List[Tuple[str, str]]:
    results = []
    span = trace.get_current_span()
    partial_func_of_fetch_text_content_from_url = partial(fetch_text_content_from_url, count=count)
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = executor.map(partial_func_of_fetch_text_content_from_url, url_list)
        for feature in futures:
            results.append(feature)
    span.set_attribute("search_results_from_url", str(results))
    return results


@tracer.start_as_current_span(name="get_wiki_url")
# Function to get Wikipedia URL for a given entity
def get_wiki_url(entity: str, count: int = 2) -> List[str]:
    # Send a request to the URL
    span = trace.get_current_span()
    span.set_attribute("query", entity)
    span.set_attribute("search_count", count)

    url = f"https://en.wikipedia.org/w/index.php?search={entity}"
    span.set_attribute("search_url", url)
    url_list = []
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # Parse the HTML content using BeautifulSoup
            soup = bs4.BeautifulSoup(response.text, "html.parser")
            mw_divs = soup.find_all("div", {"class": "mw-search-result-heading"})
            if mw_divs:  # mismatch
                result_titles = [decode_str(div.get_text().strip()) for div in mw_divs]
                result_titles = [remove_nested_parentheses(result_title) for result_title in result_titles]
                # print(f"Could not find {entity}. Similar entity: {result_titles[:count]}.")
                url_list.extend(
                    [f"https://en.wikipedia.org/w/index.php?search={result_title}" for result_title in result_titles]
                )
            else:
                page_content = [p_ul.get_text().strip() for p_ul in soup.find_all("p") + soup.find_all("ul")]
                if any("may refer to:" in p for p in page_content):
                    url_list.extend(get_wiki_url("[" + entity + "]"))
                else:
                    url_list.append(url)
        else:
            msg = (
                f"Get url failed with status code {response.status_code}.\nURL: {url}\nResponse: "
                f"{response.text[:100]}"
            )
            print(msg)
        span.set_attribute("url_list", url_list[:count])
        return url_list[:count]
    except Exception as e:
        print("Get url failed with error: {}".format(e))
        return url_list

@tracer.start_as_current_span(name="process_search_result")
# Function to process search results
def process_search_result(search_result: List[Tuple[str, str]]) -> str:
    def format(doc: dict) -> str:
        return f"Content: {doc['Content']}"
    span = trace.get_current_span()
    try:
        context = []
        for _url, content in search_result:
            context.append(
                {
                    "Content": content,
                    # "Source": url
                }
            )
        search_result = "\n\n".join([format(c) for c in context])
        span.set_attribute("search_results", search_result)
        return search_result
    except Exception as e:
        print(f"Error: {e}")
        return ""


@tracer.start_as_current_span(name="augmented_qa")
# Function to perform augmented QA
def augemented_qa(query: str, context: str) -> str:
    span = trace.get_current_span()
    span.set_attribute("query", query)
    span.set_attribute("context", context)
    # span.add_event(
    #     name="gen_ai.evaluation.relevance",
    #     attributes={
    #         "gen_ai.response.id": str(uuid.uuid4()),
    #         "gen_ai.evaluation.score": 2,
    #     }
    # )
    system_message = system_message_template.render(contexts=context)

    messages = [{"role": "system", "content": system_message}, {"role": "user", "content": query}]

    with AzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    ) as client:
        response = client.chat.completions.create(
            model=os.environ.get("AZURE_OPENAI_DEPLOYMENT"), messages=messages, temperature=0.7, max_tokens=800
        )
        # span.set_attribute("response", response.choices[0].message.content)
        return response.choices[0].message.content


# Function to ask Wikipedia


class Response(TypedDict):
    response: str
    context: str
    metadata: dict

@gen_ai_trace(tracer, "ask_wiki")
# @tracer.start_as_current_span(name="ask_wiki")
def ask_wiki(*, query: str, **kwargs) -> Response:
    span = trace.get_current_span()
    url_list = get_wiki_url(query, count=2)
    search_result = search_result_from_url(url_list, count=10)
    context = process_search_result(search_result)
    response = augemented_qa(query, context)
    response_id = str(uuid.uuid4())
    span.set_attribute("gen_ai.response.id", response_id)
    current_ctx = span.get_span_context()
    metadata = {
        "trace_id": current_ctx.trace_id,
        "span_id": current_ctx.span_id,
        "trace_flags": current_ctx.trace_flags,
        "response_id": response_id
    }

    return {"response": response, "context": str(context), "metadata": metadata}


# Main function
if __name__ == "__main__":
    print(ask_wiki("Who is the president of the United States?"))
