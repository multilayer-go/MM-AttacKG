# -*- coding: utf-8 -*-
import json
import threading
from utils.api_connector import ask_with_onlyText
from utils.api_connector import ask_with_imgANDtext_retry
import os


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
# Answer Generation
# ---------------------------------------------------------------------------

def get_first_ans(pic_file, f_ques_pool):
    """Generate initial answers for all questions using the multimodal LLM."""
    pic_in_context=get_in_context(pic_file)
    cti_outline = get_outline(pic_file)

    first_ans_list = [None] * len(f_ques_pool)  # Pre-allocate answer list
    lock = threading.Lock()  # Thread synchronization lock

    def process_question(q, index):
        # Prompt for the LLM to generate initial answers based on each question and image
        ask_to_LLM = f"""
[Task]
This image is from a cyber threat intelligence article. The provided [In-context of the image] is the in-context of the image in this cyber threat intelligence article. The provided [CTI Summary] is a summary of the Cyber Threat Intelligence article that contains this image. Please answer the following question based on the content of this image,  [In-context of the image] and [CTI Summary]. Please follow the [Rules] in your answer:
[Rules]
Rule 1: Your answer should be a single, concise sentence.
Rule 2: The content of the image must prevail when answering the question, and the entities and relationships involved in the answer can be referred to [In-context of the image] and [CTI Summary].
Rule 3: Your answer must include a topic phrase that is specific to the question. For example:
  - If the question is "What is the possible source of the image?", your answer should include "The possible source is."
  - If the question is "What are the different operating systems mentioned in the image?", your answer should include "The different operating systems are."
Rule 4: Only provide the direct answer to the question. Do not provide explanations or reasons for uncertainty.
[Question]
{q}
[In-context of the image]
{pic_in_context}
[CTI Summary]
{cti_outline}
"""
        try:
            # Call the ask_with_imgANDtext function, which is synchronous
            temp_ans = ask_with_imgANDtext_retry(pic_file, ask_to_LLM)
            # Use thread lock to protect access to first_ans_list
            with lock:
                # Place the answer at the correct index position
                first_ans_list[index] = temp_ans
        except Exception as e:
            print(f"Error processing question: {q}, Error: {e}")
            with lock:
                first_ans_list[index] = "Error in answer generation"

    threads = []
    # Create a thread for each question with its index
    for i, q in enumerate(f_ques_pool):
        thread = threading.Thread(target=process_question, args=(q, i))
        threads.append(thread)
        thread.start()
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    print("\nInitial answers:\n", first_ans_list)
    return first_ans_list



# Process all images in a CTI report
def process_answers_from_questions(input_file, output_file, picture_folder):
    with open(input_file, 'r', encoding='utf-8') as infile:
        questions_data = json.load(infile)

    answers_data = {"pictures": []}  # Store all images and their Q&A pairs

    # Iterate over all images and their questions
    for picture in questions_data['pictures']:
        img_name = picture['name']
        pic_type = picture['pic_type']
        img_path = os.path.join(picture_folder, img_name)  # Construct the full image path
        questions = [q['question'] for q in picture['questions']]

        # Generate answers for each image
        print(f"\nProcessing image: {img_name}")
        answers = get_first_ans(img_path, questions)  # Pass full file path

        # Save questions and answers
        questions_and_answers = []
        for question, answer in zip(questions, answers):
            questions_and_answers.append({
                "question": question,
                "answer": answer
            })

        # Add image and answers to output
        answers_data["pictures"].append({
            "name": img_name,
            "pic_type": pic_type,
            "questionsANDanswers": questions_and_answers
        })

    # Write answers to output file
    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(answers_data, outfile, indent=4, ensure_ascii=False)

    print(f"All answers saved to {output_file}")



if __name__ == "__main__":
    input_file = "../dataCTI/00/process/JSONstep1_Questions.json"  # Input file path (Questions.json)
    output_file = "../dataCTI/00/process/JSONstep2_Answers.json"  # Output file path (Answers.json)
    picture_folder = "../dataCTI/00/picture"  # Path to the image folder

    # Execute the function
    # process_answers_from_questions(input_file, output_file, picture_folder)
