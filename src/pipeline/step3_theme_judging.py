# -*- coding: utf-8 -*-
import json
import os
import threading
from pipeline.step1_question_generation import get_ques_seed
from utils.api_connector import ask_with_onlyText_retry
from utils.api_connector import ask_with_imgANDtext


# ---------------------------------------------------------------------------
# Domain Relevance Filtering (Question-only)
# ---------------------------------------------------------------------------

def get_fit_theme_Q_index(ques_seed, f_ques_pool):
    """Determine which questions are relevant to the cybersecurity domain."""
    Q_fit_theme = []
    lock = threading.Lock()  # Thread synchronization lock
    # # Iterate over each question in the pool; if the question is in the seed list, add its index directly
    # for index, question in enumerate(f_ques_pool):
    #     if question in ques_seed:
    #         Q_fit_theme.append(index)
    # Get remaining questions not in seed list, starting after seeds
    def process_question(q, index):
        # Prompt for the LLM to determine if the question is domain-relevant
        ask_to_LLM = f"""
[Task]
Determine whether the possible answer to the following question is related to the domain of network security or is useful for network threat analysis. Please follow these rules in your answer:
[Rules]
Rule 1: If the answer is relevant to network security or helps with network threat analysis, respond with exactly "pertinent".
Rule 2: If the answer is not related to network security or does not help with network threat analysis, respond with exactly "irrelevant".
Rule 3: Your response must be exactly one of the above two words with no additional text, punctuation, or explanation.
Rule 4: Regardless of any uncertainty, you must always and only provide one of the options: "pertinent" or "irrelevant".
[Question]
{q}
"""
        try:
            # Call LLM to determine if question is domain-relevant
            res = ask_with_onlyText_retry(ask_to_LLM)
            # print(res)
            if "pertinent" in res:
                # Use lock for thread-safe access to shared list
                with lock:
                    Q_fit_theme.append(index)
        except Exception as e:
            print(f"Error processing question: {q}, Error: {e}")
    threads = []
    # Create a thread for each question
    for i, q in enumerate(f_ques_pool[0:], start=0):
        thread = threading.Thread(target=process_question, args=(q, i))
        threads.append(thread)
        thread.start()
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    Q_fit_theme.sort()
    print("\nQuestion indices matching domain criteria:\n", Q_fit_theme)
    return Q_fit_theme


# ---------------------------------------------------------------------------
# Domain Relevance Filtering (Question + Answer)
# ---------------------------------------------------------------------------

def get_fit_theme_QA_index(ques_seed, f_ques_pool, first_ans):
    """Determine which Q&A pairs are relevant to the cybersecurity domain."""
    QA_fit_theme = []
    lock = threading.Lock()  # Lock object for thread synchronization

    # # Iterate over each question in the pool; if the question is in the seed list, add its index directly
    # for index, question in enumerate(f_ques_pool):
    #     if question in ques_seed:
    #         QA_fit_theme.append(index)
    # Use multithreading to evaluate remaining questions (combined with answers when not in seed list)
    def process_question_answer(q, a, original_index):
        ask_to_LLM = f"""
[Task]
Determine whether the following answer is relevant to the domain of network security or useful for network threat analysis. Please follow these rules in your answer:
[Rules]
Rule 1: If the answer is relevant to network security or aids in network threat analysis, respond with exactly "pertinent".
Rule 2: If the answer is not relevant to network security or does not aid in network threat analysis, respond with exactly "irrelevant".
Rule 3: Your response must be exactly one of the above two words with no additional text, punctuation, or explanation.
Rule 4: Regardless of any uncertainty, you must always and only provide one of the options: "pertinent" or "irrelevant".
[Question]
{q}
[Answer]
{a}
"""
        try:
            res = ask_with_onlyText_retry(ask_to_LLM)
            # print(res)
            if "pertinent" in res:
                with lock:
                    QA_fit_theme.append(original_index)  # Preserve original ordering
        except Exception as e:
            print(f"Error processing question-answer pair: {q} - {a}, Error: {e}")
    threads = []
    # Iterate over questions and launch threads
    for i, (q, a) in enumerate(zip(f_ques_pool[0:], first_ans[0:]), start=0):
        thread = threading.Thread(target=process_question_answer, args=(q, a, i))
        threads.append(thread)
        thread.start()
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    print("\nQ&A pair indices matching domain criteria:\n", QA_fit_theme)
    return QA_fit_theme


# ---------------------------------------------------------------------------
# Union of Domain-Relevant Indices
# ---------------------------------------------------------------------------

def get_combined_fit_theme(Q_fit_theme, QA_fit_theme):
    """Combine Q-only and QA-based domain relevance indices (union)."""
    # Merge and deduplicate
    combined_fit_theme = list(set(Q_fit_theme) | set(QA_fit_theme))
    # Preserve original order
    combined_fit_theme.sort(key=lambda x: (Q_fit_theme.index(x) if x in Q_fit_theme else float('inf'),
                                           QA_fit_theme.index(x) if x in QA_fit_theme else float('inf')))
    print("\nFinal domain-relevant indices:\n", combined_fit_theme)
    return combined_fit_theme



# Process all images in a CTI report
def process_labels_from_answers(input_file, output_file, picture_folder):
    with open(input_file, 'r', encoding='utf-8') as infile:
        answers_data = json.load(infile)

    labels_data = {"pictures": []}  # Store all images with Q&A and labels

    # Iterate over each image and its Q&A pairs
    for picture in answers_data['pictures']:
        img_name = picture['name']
        pic_type = picture['pic_type']
        img_path = os.path.join(picture_folder, img_name)  # Full image path
        questions_and_answers = picture['questionsANDanswers']

        # Get question seeds for this image type
        # pic_type = judge_pic_type(img_path)
        ques_seed = get_ques_seed(pic_type)

        f_ques_pool = [q['question'] for q in questions_and_answers]  # Extract all questions
        first_ans = [q['answer'] for q in questions_and_answers]  # Extract all answers

        # Get domain-relevant question indices (question-only)
        Q_fit_theme = get_fit_theme_Q_index(ques_seed, f_ques_pool)

        # Get domain-relevant Q&A pair indices
        QA_fit_theme = get_fit_theme_QA_index(ques_seed, f_ques_pool, first_ans)

        # Combine both sets of indices
        combined_fit_theme = get_combined_fit_theme(Q_fit_theme, QA_fit_theme)

        # Build final list with domain labels for each Q&A pair
        questions_and_answers_and_labels = []
        for i, (q, a) in enumerate(zip(f_ques_pool, first_ans)):
            # Determine each question's labels
            qlabel1 = "yes" if i in Q_fit_theme else "no"  # Question-only judgment
            qlabel2 = "yes" if i in QA_fit_theme else "no"  # Q&A pair judgment
            qlabel = "yes" if i in combined_fit_theme else "no"  # Combined judgment

            questions_and_answers_and_labels.append({
                "question": q,
                "answer": a,
                "qlabel1": qlabel1,
                "qlabel2": qlabel2,
                "qlabel": qlabel
            })

        # Add image data with labels
        labels_data["pictures"].append({
            "name": img_name,
            "pic_type": pic_type,
            "questionsANDanswersANDqlabels": questions_and_answers_and_labels
        })

    # Write label data to output file
    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(labels_data, outfile, indent=4, ensure_ascii=False)

    print(f"All domain labels saved to {output_file}")


if __name__ == "__main__":
    input_file = "../dataCTI/00/Answers.json"  # Input file path (Answers.json)
    output_file = "../dataCTI/00/QLabels.json"  # Output file path (Labels.json)
    picture_folder = "../dataCTI/00/picture"  # Path to the image folder

    # Execute the function
    process_labels_from_answers(input_file, output_file, picture_folder)


