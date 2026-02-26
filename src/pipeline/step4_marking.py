# -*- coding: utf-8 -*-
"""
Step 4: Answer Marking

Evaluates the quality of each answer using a separate LLM
as an independent judge. The system provides an extensible evaluation
interface that supports third-party LLMs, but due to service access
restrictions, only domestic models (DashScope/Qwen) are used by default.
Answers are scored as "excellent", "good", "satisfactory", or "failing"
based on accuracy, consistency, completeness, and relevance criteria.
"""

import json
import os
import threading
import requests
import base64
import random
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import multiprocessing


# ---------------------------------------------------------------------------
# Marking API (uses a separate LLM endpoint for evaluation)
# ---------------------------------------------------------------------------

def encode_image(image_path):
    """Encode an image file to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def mark_use_evaluator(img_path, prompt):
    """
    Send an image + prompt to the evaluation LLM for answer scoring.

    Configure via environment variables:
        - EVAL_API_KEY: API key for the evaluation model (defaults to DASHSCOPE_API_KEY)
        - EVAL_API_URL: API endpoint URL
        - EVAL_MODEL: Model name (default: qwen2.5-72b-instruct)

    The interface supports third-party LLMs, but due to service access
    restrictions, only domestic models (DashScope/Qwen) are used by default.

    Args:
        img_path: Path to the image file.
        prompt: Evaluation prompt containing question, answer, and rubric.

    Returns:
        The evaluator's response (typically a quality label).

    Raises:
        requests.exceptions.RequestException: If the API request fails.
    """
    api_key = os.getenv("EVAL_API_KEY", os.getenv("DASHSCOPE_API_KEY", ""))
    model = os.getenv("EVAL_MODEL", "qwen2.5-72b-instruct")
    url = os.getenv("EVAL_API_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")

    if not api_key:
        raise ValueError(
            "No evaluation API key configured. "
            "Set EVAL_API_KEY or DASHSCOPE_API_KEY environment variable."
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    base64_image = encode_image(img_path)

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
    ]

    greeting_keywords = ['assist you', 'have any coding question']

    def is_greeting_response(content):
        content_lower = content.lower()
        return any(greeting in content_lower for greeting in greeting_keywords)

    try:
        retry_count = 0
        max_retries = 5

        while retry_count < max_retries:
            response = requests.post(
                url, headers=headers,
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": 0,
                    "top_p": 1,
                    "seed": 42
                }
            )

            if response.status_code == 200:
                response_data = response.json()
                content = response_data['choices'][0]['message']['content']
                if is_greeting_response(content):
                    print(f"Received greeting response: '{content}', retrying...")
                    retry_count += 1
                    continue
                else:
                    return content
            else:
                error_message = f"Request failed: {response.status_code} {response.text}"
                raise requests.exceptions.RequestException(error_message)

        raise Exception("Max retries reached, still receiving greeting responses")

    except requests.exceptions.RequestException as e:
        print(f"Error caught: {e}")
        raise e


def _mark_worker(pic_file, ask_to_LLM, output_queue):
    """Worker process for marking API calls."""
    try:
        result = mark_use_evaluator(pic_file, ask_to_LLM)
        output_queue.put(('result', result))
    except Exception as e:
        output_queue.put(('exception', e))


def mark_use_evaluator_retry(pic_file, ask_to_LLM,
                             max_retries=9, base_delay=1, timeout=120):
    """
    Call mark_use_evaluator with automatic retry and timeout handling.

    Args:
        pic_file: Path to the image file.
        ask_to_LLM: Evaluation prompt.
        max_retries: Maximum retry attempts.
        base_delay: Base delay for exponential backoff.
        timeout: Timeout per attempt in seconds.

    Returns:
        The evaluator's response, or None if all retries fail.
    """
    retries = 0
    while retries < max_retries:
        output_queue = multiprocessing.Queue()
        process = multiprocessing.Process(
            target=_mark_worker, args=(pic_file, ask_to_LLM, output_queue)
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


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def get_in_context(pic_file):
    """Retrieve the in-context text for the given image from its CTI report."""
    pic_filename = os.path.basename(pic_file)
    report_dir = os.path.dirname(os.path.dirname(pic_file))
    original_json_path = os.path.join(report_dir, "original", "In-context.json")
    in_context_text = ""
    with open(original_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for item in data:
        if item.get("Image_name", "") == pic_filename:
            in_context_text = item.get("In-context", "")
            break
    return in_context_text


def get_outline(pic_file):
    """Retrieve the CTI report outline for the given image."""
    report_dir = os.path.dirname(os.path.dirname(pic_file))
    original_json_path = os.path.join(report_dir, "original", "outline.json")
    with open(original_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    outline_text = data.get("outline", "")
    return outline_text


# ---------------------------------------------------------------------------
# Answer Marking Logic
# ---------------------------------------------------------------------------

def get_mark(pic_file, ques_list, ans_list):
    """
    Score each answer's quality using the evaluation LLM.

    Each answer is evaluated on four criteria (accuracy, consistency,
    completeness, relevance) and assigned one of: "excellent", "good",
    "satisfactory", or "failing".

    Args:
        pic_file: Path to the image file.
        ques_list: List of questions.
        ans_list: List of corresponding answers.

    Returns:
        List of quality labels (same length as ans_list).
    """
    pic_in_context = get_in_context(pic_file)
    cti_outline = get_outline(pic_file)

    mark_list = [None] * len(ans_list)
    lock = threading.Lock()

    def process_answer(q, a, index):
        ask_to_LLM = f"""
[Task]
This image is from a cyber threat intelligence article. The provided [In-context of the image] is the in-context of the image in this cyber threat intelligence article. The provided [CTI Summary] is a summary of the Cyber Threat Intelligence article that contains this image. Based on the content of the image and with reference to the [In-context of the image] and [CTI Summary], evaluate the quality of the following [Description] in terms of accuracy, consistency, completeness, and relevance. Rate the [Description] using one of the following labels: "excellent", "good", "satisfactory", or "failing". Please follow these rules in your answer:
[Rules]
Rule 1: Evaluate the [Description] using the following four criteria:
- Accuracy: Accuracy represents whether the [Description] accurately answers the [Question].
-- Score 1: The [Description] is entirely incorrect to the question and contains severely misleading information.
-- Score 2: The [Description] is partially correct but includes significant errors or irrelevant content.
-- Score 3: The [Description] is mostly accurate but contains minor errors or ambiguous phrasing.
-- Score 4: The [Description] is accurate and correct but lacks direct image references.
-- Score 5: The [Description] is fully accurate, unambiguous, and directly supported by the image content.
- Consistency: Consistency represents whether the [Description] maintains content relevance to the image information.
-- Score 1: The [Description] completely contradicts or is unrelated to the image information.
-- Score 2: The [Description] includes limited relevant details, but most content deviates from the image information.
-- Score 3: The [Description] partially aligns with the image information but contains irrelevant or redundant content.
-- Score 4: The [Description] closely adheres to the image information, with only minimal unrelated content.
-- Score 5: The [Description] is entirely based on the image information, with no extraneous or redundant elements.
- Completeness: Completeness represents whether the [Description] adequately addresses the needs of the [Question].
-- Score 1: The [Description] fails to address any critical aspects of the question, omitting all essential information.
-- Score 2: The [Description] addresses only a subset of the question, omitting most key details.
-- Score 3: The [Description] broadly covers the question's requirements but lacks minor details.
-- Score 4: The [Description] comprehensively addresses the question, with only negligible omissions of minor details.
-- Score 5: The [Description] fully addresses all requirements of the question, providing thorough details.
- Relevance: Relevance represents whether the [Description] is relevant to the cybersecurity field or useful for cyber threat analysis.
-- Score 1: The [Description] is entirely unrelated to cybersecurity and provides no value for threat analysis.
-- Score 2: The [Description] has marginal relevance, requiring substantial inference to connect to threat analysis.
-- Score 3: The [Description] partially relates to cybersecurity but lacks explicit ties to practical applications.
-- Score 4: The [Description] directly aligns with cybersecurity and offers moderate analytical value for threat analysis.
-- Score 5: The [Description] focuses heavily on cybersecurity and provides actionable insights into threat analysis.
Rule 2: Apply the following rating scale based on the overall quality:
- "excellent": The [Description] scored more than 16 on all four criteria combined.
- "good": The [Description] scored between 12 and 16 on the sum of the four criteria.
- "satisfactory": The [Description] scored between 8 and 12 on the sum of the four criteria.
- "failing": The [Description] scored less than 8 on the sum of the four criteria.
Rule 3: The content of the image must prevail when evaluating [Description], and [In-context of the image] and [CTI Summary] may be used as a reference.
Rule 4: If there are statements in the [Description] such as unknown, no details, not mentioned, etc., mark it as "failing".
Rule 5: Your answer should be a single word: either "excellent", "good", "satisfactory", or "failing", and do not include other characters, such as quotation marks.
[Question]
{q}
[Description]
{a}
[In-context of the image]
{pic_in_context}
[CTI Summary]
{cti_outline}
"""
        try:
            temp_mark = mark_use_evaluator_retry(pic_file, ask_to_LLM)
            with lock:
                mark_list[index] = temp_mark
        except Exception as e:
            print(f"Error processing answer: {a}, Error: {e}")
            with lock:
                mark_list[index] = "failing"

    threads = []
    for i, (q, a) in enumerate(zip(ques_list, ans_list)):
        thread = threading.Thread(target=process_answer, args=(q, a, i))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

    print("\nEvaluator scoring results:\n", mark_list)
    return mark_list


# ---------------------------------------------------------------------------
# Main Processing Function
# ---------------------------------------------------------------------------

def process_marks_from_labels(input_file, output_file, picture_folder):
    """
    Read labeled Q&A data and add quality marks to each answer.

    Args:
        input_file: Path to input JSON (from Step 3).
        output_file: Path to output JSON with marks added.
        picture_folder: Path to the image directory.
    """
    with open(input_file, 'r', encoding='utf-8') as infile:
        labels_data = json.load(infile)

    mark_data = {"pictures": []}

    for picture in labels_data['pictures']:
        img_name = picture['name']
        pic_type = picture['pic_type']
        img_path = os.path.join(picture_folder, img_name)
        questions_and_answers_and_labels = picture['questionsANDanswersANDqlabels']

        ques_list = [qa['question'] for qa in questions_and_answers_and_labels]
        ans_list = [qa['answer'] for qa in questions_and_answers_and_labels]

        marks = get_mark(img_path, ques_list, ans_list)

        questions_and_answers_and_labels_and_marks = []
        for i, (qa, mark) in enumerate(zip(questions_and_answers_and_labels, marks)):
            questions_and_answers_and_labels_and_marks.append({
                "question": qa['question'],
                "answer": qa['answer'],
                "qlabel1": qa['qlabel1'],
                "qlabel2": qa['qlabel2'],
                "qlabel": qa['qlabel'],
                "mark": mark
            })

        mark_data["pictures"].append({
            "name": img_name,
            "pic_type": pic_type,
            "questionsANDanswersANDqlabelsANDmark": questions_and_answers_and_labels_and_marks
        })

    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(mark_data, outfile, indent=4, ensure_ascii=False)

    print(f"All answer marks saved to {output_file}")


if __name__ == "__main__":
    input_file = "../dataCTI/00/QLabels.json"
    output_file = "../dataCTI/00/Mark.json"
    picture_folder = "../dataCTI/00/picture"
    process_marks_from_labels(input_file, output_file, picture_folder)
