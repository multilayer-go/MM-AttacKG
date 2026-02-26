# -*- coding: utf-8 -*-
"""
API Connector Module

Provides unified interfaces for calling LLM APIs (text-only and multimodal).
Supports DashScope (Qwen) and OpenAI-compatible APIs with automatic retry,
timeout handling, and exponential backoff.
"""

import requests
import json
import os
import dashscope
from openai import OpenAI
import time
import random
import multiprocessing


# ---------------------------------------------------------------------------
# Core API Functions (configurable via environment variables)
# ---------------------------------------------------------------------------

def ask_with_onlyText(text, role='You are a helpful assistant.'):
    """
    Send a text-only query to the LLM and return the response.

    Uses DashScope (Qwen) API by default. Configure via environment variables:
        - DASHSCOPE_API_KEY: Your DashScope API key
        - DASHSCOPE_BASE_URL: API base URL (optional)
        - TEXT_MODEL: Model name (default: qwen2.5-72b-instruct)

    Args:
        text: The question or prompt text.
        role: System role prompt for the LLM.

    Returns:
        The LLM's response content as a string.

    Raises:
        requests.exceptions.RequestException: If the API request fails.
    """
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url=os.getenv("DASHSCOPE_BASE_URL",
                           "https://dashscope.aliyuncs.com/compatible-mode/v1"),
    )
    model = os.getenv("TEXT_MODEL", "qwen2.5-72b-instruct")

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {'role': 'system', 'content': role},
                {'role': 'user', 'content': text}
            ],
            temperature=0,
            top_p=1,
            seed=42,
        )

        if completion.choices:
            return completion.choices[0].message.content
        else:
            error_message = "Request failed: empty response"
            raise requests.exceptions.RequestException(error_message)

    except requests.exceptions.RequestException as e:
        print(f"Error caught: {e}")
        raise e


def ask_with_imgANDtext(img, question):
    """
    Send a multimodal query (image + text) to the LLM and return the response.

    Uses DashScope multimodal API by default. Configure via environment variables:
        - DASHSCOPE_API_KEY: Your DashScope API key
        - VISION_MODEL: Vision model name (default: qwen2.5-vl-72b-instruct)

    Args:
        img: Path or URL of the image.
        question: The question about the image.

    Returns:
        The LLM's response content as a string.

    Raises:
        requests.exceptions.RequestException: If the API request fails.
    """
    model = os.getenv("VISION_MODEL", "qwen2.5-vl-72b-instruct")

    messages = [
        {
            "role": "user",
            "content": [
                {"image": img},
                {"text": question}
            ]
        }
    ]

    try:
        response = dashscope.MultiModalConversation.call(
            api_key=os.getenv('DASHSCOPE_API_KEY'),
            model=model,
            messages=messages,
            temperature=0,
            top_p=1,
            seed=42,
        )

        if response.status_code == 200 and response.output:
            content = response.output['choices'][0]['message']['content'][0]['text']
            return content
        else:
            error_message = f"Request failed: {response.status_code} {response}"
            raise requests.exceptions.RequestException(error_message)

    except requests.exceptions.RequestException as e:
        print(f"Error caught: {e}")
        raise e


# ---------------------------------------------------------------------------
# Retry Wrappers with Timeout and Exponential Backoff
# ---------------------------------------------------------------------------

def _worker_text(text, role, output_queue):
    """Worker process for text-only API calls."""
    try:
        result = ask_with_onlyText(text, role)
        output_queue.put(('result', result))
    except Exception as e:
        output_queue.put(('exception', e))


def ask_with_onlyText_retry(text, role='You are a helpful assistant.',
                            max_retries=20, base_delay=1, timeout=120):
    """
    Call ask_with_onlyText with automatic retry and timeout handling.

    Spawns a subprocess for each attempt so that hung API calls can be
    terminated cleanly. Implements exponential backoff on failures.

    Args:
        text: The question or prompt text.
        role: System role prompt.
        max_retries: Maximum number of retry attempts.
        base_delay: Base delay in seconds for backoff calculation.
        timeout: Timeout in seconds per attempt.

    Returns:
        The LLM's response string, or None if all retries are exhausted.
    """
    retries = 0
    while retries < max_retries:
        output_queue = multiprocessing.Queue()
        process = multiprocessing.Process(
            target=_worker_text, args=(text, role, output_queue)
        )
        process.start()
        process.join(timeout)

        if process.is_alive():
            print(f"Request timed out ({timeout}s), retrying... "
                  f"(attempt {retries + 1})")
            process.terminate()
            process.join()
            retries += 1
            time.sleep(base_delay)
        else:
            if not output_queue.empty():
                status, data = output_queue.get()
                if status == 'result':
                    return data
                elif status == 'exception':
                    e = data
                    retries += 1
                    wait_time = base_delay * (2 ** retries) + random.uniform(0, 1)
                    print(f"Request failed: {e}")
                    print(f"Waiting {wait_time:.2f}s before retry...")
                    time.sleep(wait_time)
            else:
                print(f"No result returned, retrying... (attempt {retries + 1})")
                retries += 1
                time.sleep(base_delay)

        if retries >= max_retries:
            print("Max retries reached. Please try again later.")
            return None
    return None


def _worker_img(pic_file, ask_to_LLM, output_queue):
    """Worker process for multimodal API calls."""
    try:
        result = ask_with_imgANDtext(pic_file, ask_to_LLM)
        output_queue.put(('result', result))
    except Exception as e:
        output_queue.put(('exception', e))


def ask_with_imgANDtext_retry(pic_file, ask_to_LLM,
                              max_retries=20, base_delay=1, timeout=120):
    """
    Call ask_with_imgANDtext with automatic retry and timeout handling.

    Args:
        pic_file: Path or URL of the image.
        ask_to_LLM: The prompt/question about the image.
        max_retries: Maximum number of retry attempts.
        base_delay: Base delay in seconds for backoff calculation.
        timeout: Timeout in seconds per attempt.

    Returns:
        The LLM's response string, or None if all retries are exhausted.
    """
    retries = 0
    while retries < max_retries:
        output_queue = multiprocessing.Queue()
        process = multiprocessing.Process(
            target=_worker_img, args=(pic_file, ask_to_LLM, output_queue)
        )
        process.start()
        process.join(timeout)

        if process.is_alive():
            print(f"Request timed out ({timeout}s), retrying... "
                  f"(attempt {retries + 1})")
            process.terminate()
            process.join()
            retries += 1
            time.sleep(base_delay)
        else:
            if not output_queue.empty():
                status, data = output_queue.get()
                if status == 'result':
                    return data
                elif status == 'exception':
                    e = data
                    retries += 1
                    wait_time = base_delay * (2 ** retries) + random.uniform(0, 1)
                    print(f"Request failed: {e}")
                    print(f"Waiting {wait_time:.2f}s before retry...")
                    time.sleep(wait_time)
            else:
                print(f"No result returned, retrying... (attempt {retries + 1})")
                retries += 1
                time.sleep(base_delay)

        if retries >= max_retries:
            print("Max retries reached. Please try again later.")
            return None
    return None


if __name__ == "__main__":
    # Quick test
    text = "What is the MITRE ATT&CK framework?"
    res = ask_with_onlyText_retry(text)
    print(res)

