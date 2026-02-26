# -*- coding: utf-8 -*-
import json
import os
import threading
from utils.api_connector import ask_with_onlyText
from utils.api_connector import ask_with_imgANDtext_retry
from pipeline.step4_marking import get_mark


# ---------------------------------------------------------------------------
# Context Retrieval Helpers
# ---------------------------------------------------------------------------

def get_in_context(pic_file):
    """Retrieve the in-context text for the given image from its CTI report."""
    pic_filename = os.path.basename(pic_file)
    report_dir = os.path.dirname(os.path.dirname(pic_file))
    original_json_path = os.path.join(report_dir, "original", "In-context.json")
    in_context_text = ""
    with open(original_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Strictly match the image filename
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
    outline_text=data.get("outline","")
    return outline_text


# ---------------------------------------------------------------------------
# Form 1 Refinement: Direct answer improvement (without suggestions)
# ---------------------------------------------------------------------------

def get_second_ans_withonly_preAns(pic_file, reanswer_ques, pre_ans):
    """Refine answers using only previous answers (Form 1 - no suggestions)."""
    pic_in_context = get_in_context(pic_file)
    cti_outline = get_outline(pic_file)

    second_ans_list = [None] * len(reanswer_ques)  # Pre-allocate answer list
    lock = threading.Lock()  # Thread synchronization lock

    def process_second_answer(index, question, answer):
        # Form 1: Direct refinement prompt based on previous answer
        ask_to_LLM = f"""
[Task]
This image is from a cyber threat intelligence article. The provided [In-context of the image] is the in-context of the image in this cyber threat intelligence article. The provided [CTI Summary] is a summary of the Cyber Threat Intelligence article that contains this image. Given the provided picture, [In-context of the image], [CTI Summary], the following [Question], and the [Previous unqualified answer], your task is to improve the answer. Please follow these rules in your answer:
[Rules]
Rule 1: Analyze the [Previous unqualified answer] and identify which of the following four criteria it does not meet. Your new answer should improve the answer in a way that meets all four criteria and achieves high Score:
- Accuracy: Accuracy represents whether the answer accurately answers the [Question].
-- Score 1: The answer is entirely incorrect to the question and contains severely misleading information.
-- Score 2: The answer is partially correct but includes significant errors or irrelevant content.
-- Score 3: The answer is mostly accurate but contains minor errors or ambiguous phrasing.
-- Score 4: The answer is accurate and correct but lacks direct image references.
-- Score 5: The answer is fully accurate, unambiguous, and directly supported by the image content.
- Consistency: Consistency represents whether the answer maintains content relevance to the image information.
-- Score 1: The answer completely contradicts or is unrelated to the image information.
-- Score 2: The answer includes limited relevant details, but most content deviates from the image information.
-- Score 3: The answer partially aligns with the image information but contains irrelevant or redundant content.
-- Score 4: The answer closely adheres to the image information, with only minimal unrelated content.
-- Score 5: The answer is entirely based on the image information, with no extraneous or redundant elements.
- Completeness: Completeness represents whether the answer adequately addresses the needs of the [Question].
-- Score 1: The answer fails to address any critical aspects of the question, omitting all essential information.
-- Score 2: The answer addresses only a subset of the question, omitting most key details.
-- Score 3: The answer broadly covers the question’s requirements but lacks minor details.
-- Score 4: The answer comprehensively addresses the question, with only negligible omissions of minor details.
-- Score 5: The answer fully addresses all requirements of the question, providing thorough details.
- Relevance: Relevance represents whether the answer is relevant to the cybersecurity field or useful for cyber threat analysis.
-- Score 1: The answer is entirely unrelated to cybersecurity and provides no value for threat analysis.
-- Score 2: The answer has marginal relevance, requiring substantial inference to connect to threat analysis.
-- Score 3: The answer partially relates to cybersecurity but lacks explicit ties to practical applications.
-- Score 4: The answer directly aligns with cybersecurity and offers moderate analytical value for threat analysis.
-- Score 5: The answer focuses heavily on cybersecurity and provides actionable insights into threat analysis.
Rule 2: The content of the image must prevail when answering the question, and the entities and relationships involved in the answer can be referred to [In-context of the image] and [CTI Summary].
Rule 3: Your answer should be a single, concise sentence.
Rule 4: Your answer must include a topic phrase that is specific to the question. For example:
- If the question is "What is the possible source of the image?", your answer should include "The possible source is."
- If the question is "What are the different operating systems mentioned in the image?", your answer should include "The different operating systems are."
Rule 5: Only provide the optimized answer without explaining reasons for uncertainty.
Rule 6: Ensure the optimized answer differs from the [Previous unqualified answer].
[Question]
{question}
[Previous unqualified answer]
{answer}
[In-context of the image]
{pic_in_context}
[CTI Summary]
{cti_outline}
"""
        try:
            temp_ans = ask_with_imgANDtext_retry(pic_file, ask_to_LLM)
            with lock:
                second_ans_list[index] = temp_ans
        except Exception as e:
            print(f"Error processing question {index}: {e}")
            with lock:
                second_ans_list[index] = "Error generating second answer"

    # Create thread list
    threads = []
    for i, (question, answer) in enumerate(zip(reanswer_ques, pre_ans)):
        thread = threading.Thread(target=process_second_answer, args=(i, question, answer))
        threads.append(thread)
        thread.start()
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    print("\nRefined answers:\n", second_ans_list)
    return second_ans_list


# ---------------------------------------------------------------------------
# Iterative Optimization Process (Form 1)
# ---------------------------------------------------------------------------
def process_image_optimization_form1(img_path, questions_answers_data):
    """
    Iteratively optimize all questions for each image (Form 1) until the stop condition is met.
    Form 1 optimization relies only on previous answers, without using external suggestions.
    """
    iterations_data = []  # Store iteration data for all questions of each image

    # Initialize records for all questions (even "excellent" ones)
    iteration_details_map = {}
    reanswer_ques = []
    pre_ans = []

    for qa in questions_answers_data:
        question = qa['question']
        answer = qa['answer']
        mark = qa['mark']
        qlabel1 = qa['qlabel1']
        qlabel2 = qa['qlabel2']
        qlabel = qa['qlabel']

        # Initialize all questions first, recording the original mark
        iteration_details_map[question] = {
            'question': question,
            'answer': answer,
            'qlabel1': qlabel1,
            'qlabel2': qlabel2,
            'qlabel': qlabel,
            'mark': mark,  # Preserve the initial mark
            'iteration': []  # Record all iteration data for this question
        }

        # Only optimize non-"excellent" questions
        if mark in ["good", "satisfactory", "failing"]:
            reanswer_ques.append(question)
            pre_ans.append(answer)

    iteration_count = 0  # Iteration count
    while iteration_count < 4 and len(reanswer_ques) > 0:
        print(f"Iteration round {iteration_count + 1}: processing {len(reanswer_ques)} questions")

        # 1. Generate new answers using previous answers (Form 1)
        new_answers = get_second_ans_withonly_preAns(img_path, reanswer_ques, pre_ans)

        # 2. Evaluate new answers
        new_marks = get_mark(img_path, reanswer_ques, new_answers)

        # 3. Record iteration results
        to_remove = []
        for i, question in enumerate(reanswer_ques):
            # Record each round's optimization results in the iteration field
            iteration_details_map[question]['iteration'].append({
                'count': iteration_count + 1,
                'answer': new_answers[i],
                'mark': new_marks[i]
            })

            # 4. Remove questions that reached "excellent" quality
            if new_marks[i] == "excellent":
                to_remove.append(i)

        # 5. Remove completed questions
        for index in sorted(to_remove, reverse=True):
            del reanswer_ques[index]
            del pre_ans[index]

        # 6. Increment iteration count
        iteration_count += 1

    # All questions must be recorded (even those not optimized)
    for qa in questions_answers_data:
        iterations_data.append(iteration_details_map[qa['question']])

    return iterations_data



# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------

def main_form1(input_file, output_file, picture_folder):
    """
    Read Mark.json and execute the answer optimization iteration process (Form 1),
    then save the results to Iteration_Form1.json.

    Args:
        input_file: str -> Input file path (Mark.json)
        output_file: str -> Output file path (Iteration_Form1.json)
        picture_folder: str -> Path to the image folder
    """
    # Read the Mark.json file
    with open(input_file, 'r', encoding='utf-8') as infile:
        mark_data = json.load(infile)

    # Initialize final results
    final_results = {
        "pictures": []
    }

    # Iterate over each image
    for picture in mark_data['pictures']:
        img_file = picture['name']  # This is the filename
        pic_type = picture['pic_type']
        img_path = os.path.join(picture_folder, img_file)  # Construct the full path
        questions_answers_data = picture['questionsANDanswersANDqlabelsANDmark']

        # Process the image optimization (Form 1)
        iterations_data = process_image_optimization_form1(img_path, questions_answers_data)

        # Save iteration results to final_results
        final_results["pictures"].append({
            'name': img_file,  # Keep the original filename
            'pic_type': pic_type,
            'questionsANDanswersANDqlabelsANDmarkANDiteration': iterations_data
        })

    # Save results to Iteration_Form1.json
    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(final_results, outfile, indent=4, ensure_ascii=False)

    print(f"Optimization results saved to {output_file}")




if __name__ == "__main__":
    # Set input and output file paths
    input_file = "../dataCTI/00/Mark.json"
    output_file = "../dataCTI/00/Iteration_Form1.json"
    picture_folder = "../dataCTI/00/picture"

    # Execute the main function
    main_form1(input_file, output_file, picture_folder)


