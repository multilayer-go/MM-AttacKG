# -*- coding: utf-8 -*-
import os
import json
from utils.api_connector import ask_with_onlyText_retry
from utils.api_connector import ask_with_imgANDtext_retry


# ---------------------------------------------------------------------------
# Image Classification
# ---------------------------------------------------------------------------
def judge_pic_type(pic_file):
    # Prompt for the LLM to classify the image type
    ask_to_LLM = """
[Task]
Classify the following image from cyber threat intelligence into one of the 7 categories listed below. Provide only the category name as your answer.
Categories: Attack Flow or Intelligence Structure, Malware Code, Application Tool Screenshot, Data Table, Charts and Data Visualization, File Paths and Names, Descriptive Image and Content Explanation
Please learn from the output examples in the [Examples of Output] section and follow the [Rules] provided below when answering.
[Rules]
Rule 1: Carefully analyze the image to identify its primary content.
Rule 2: Match the content to the most relevant category from the list above.
Rule 3: Give only the name of the type in your answer and do not include other characters, such as quotation marks. (e.g.,Charts and Data Visualization,Application Tool Screenshot).
Rule 4: Do not provide additional contents in your response.

[Examples of Output]
Example 1 of correct output:
Malware Code

Example 2 of correct output:
File Paths and Names

Example of wrong output and its wrong reason:
I can see this image contains JavaScript zCode with function definitions, variable assignments, and operations.
Malware Code
Wrong reason: The output contains something other than the category.
"""
    pic_type = ask_with_imgANDtext_retry(pic_file, ask_to_LLM)
    pic_type = pic_type.strip()
    print(f"\nImage {pic_file} classified as:\n", pic_type)
    return pic_type


# ---------------------------------------------------------------------------
# Question Seed Selection
# ---------------------------------------------------------------------------
def get_ques_seed(LLM_response):
    pic_type='No type'
    if 'Attack Flow or Intelligence Structure' in LLM_response:
        pic_type='Attack Flow or Intelligence Structure'
    elif 'Malware Code' in LLM_response:
        pic_type = 'Malware Code'
    elif 'Application Tool Screenshot' in LLM_response:
        pic_type = 'Application Tool Screenshot'
    elif 'Data Table' in LLM_response:
        pic_type = 'Data Table'
    elif 'Charts and Data Visualization' in LLM_response:
        pic_type = 'Charts and Data Visualization'
    elif 'File Paths and Names' in LLM_response:
        pic_type = 'File Paths and Names'
    elif 'Descriptive Image and Content Explanation' in LLM_response:
        pic_type = 'Descriptive Image and Content Explanation'
    ques_seed_list=get_ques_seed_(pic_type)
    return ques_seed_list
def get_ques_seed_(pic_type):
    question_seed_list = {
        "Attack Flow or Intelligence Structure": [
            "What is the main content of the image?",
            "What are the possible uses of the image?",
            "What are the possible attack techniques involved in the image?",
            "What is the sequential relationship of the processes in the image?",
            "What are the possible targets of attack in the image?"
        ],
        "Malware Code": [
            "What is the main content of code in the image?",
            "What are the possible uses of the image?",
            "What are the possible attack techniques involved in the image?",
            "What is the possible function of the Code in the image?",
            "What are the possible variables in the Code in the image?",
        ],
        "Application Tool Screenshot": [
            "What is the main content of the image?",
            "What are the possible uses of the image?",
            "What are the possible attack techniques involved in the image?",
            "What is the key highlighted information in the picture?",
        ],
        "Data Table": [
            "What is the main content of the image?",
            "What are the possible uses of the image?",
            "What are the possible attack techniques involved in the image?",
            "What are the fields highlighted in the image?",
            "What are the possible informations relevant to malicious activity in the image?"
        ],
        "Charts and Data Visualization": [
            "What is the main content of the image?",
            "What are the possible uses of the image?",
            "What are the trends reflected in the image?",
            "What are the conclusions that can be made based on the image?",
        ],
        "File Paths and Names": [
            "What is the main content of the image?",
            "What are the possible uses of the image?",
            "What are the possible attack techniques involved in the image?",
            "What paths are included in the image?"
        ],
        "Descriptive Image and Content Explanation": [
            "What is the main content of the image?",
            "What are the possible uses of the image?",
            "What are the possible attack techniques involved in the image?"
        ]
    }
    pic_type = pic_type.strip()
    ques_seed_list = question_seed_list.get(pic_type)
    print("\nQuestion seeds:\n", ques_seed_list)
    return ques_seed_list


# ---------------------------------------------------------------------------
# Phase 1: Question Pool Generation from Seeds
# ---------------------------------------------------------------------------
# def check_format(wait_for_check_str):
#     ask_to_LLM = f"""
#         Determine whether the input content conforms to the following rules:
#         Rule 1: The input content can only contain one list. The list with the format: ["What is the main content of the image?", "What is the possible source of the image?", "What role does 'TrailBlazer' infrastructure play in the context of this image?", ......]
#         Rule 2: Each question must begin and end with double quotation marks ("), If quotation marks are used inside the question, they must be single quotation marks ('). Such as: "What role does 'TrailBlazer' infrastructure play in the context of this image?"
#         input content: {wait_for_check_str}
#         If all the rules are met, output only one word "yes". If there is any rule that is not met, output "no" and explain the reason.
#         """
#     check_format = ask_with_onlyText_retry(ask_to_LLM)
#     return check_format

def get_step1_ques_pool(pic_file, ques_seed_list):
    ques_seed = '\n'.join(ques_seed_list)
    # Prompt for the LLM to generate additional aspects for information extraction
    ask_to_LLM = f"""
[Task]
You are tasked with identifying additional aspects of the image based on its content, which have not been covered by the existing set of questions. These new aspects should be phrased as questions that can help further analyze the image. Please follow these rules in your answer:
[Rules]
Rule 1: Review the list of existing questions provided and generate new questions that explore different perspectives, details, or contexts within the image.
Rule 2: Refer to the format of the given questions, which follows the pattern: "What is/are the XXX of/in the image?", "Where XXX should be replaced with a specific aspect of the image?".
Rule 3: Make a list of the following existing questions in your answers first and then add new ones one by one.
Rule 4: Each question must begin and end with double quotation marks ("), If quotation marks are used inside the question, they must be single quotation marks (').
Rule 5: Give only one list of questions in plain text format (ensure there are no other characters such as zCode block markers) in your answer with the format: ["What is the main content of the image?", "What is the possible source of the image?", "What role does 'TrailBlazer' infrastructure play in the context of this image?", ......], and nothing else.
Rule 6: Your response can contain only one list.
[Existing questions]
{ques_seed}
"""
    step1_ques_pool = ask_with_imgANDtext_retry(pic_file, ask_to_LLM)
    start_index = step1_ques_pool.find('[')
    end_index = step1_ques_pool.rfind(']')
    if start_index != -1 and end_index != -1 and end_index > start_index:
        print("\nPhase 1 question pool:\n", step1_ques_pool[start_index:end_index+1])
        return step1_ques_pool[start_index:end_index+1]
    else:
        return "Please retry"


# ---------------------------------------------------------------------------
# Knowledge Graph Description
# ---------------------------------------------------------------------------
def get_KG_description(KG_file):
    with open(KG_file, 'r') as file:
        data = json.load(file)
    # Extract the "triplets" section
    triplets = data[0].get("triplets", [])
    # Convert the triplets list to a string, keeping the "triplets" key
    triplets_str = '"triplets": ' + json.dumps(triplets)
    # Prompt for the LLM to generate the KG description
    ask_to_LLM = f"""
[Task]
The following triplets represent the extracted entities and relationships from a cyber threat intelligence report. These triplets collectively form a knowledge graph (KG). Please analyze the relationships between the entities in this KG and provide a detailed, coherent summary of what the KG describes. Please follow these rules in your answer:
[Rules]
Rule 1: Focus on analyzing the connections and interactions between the entities in the knowledge graph.
Rule 2: Identify key patterns, insights, and narratives the KG reveals about the cyber threat intelligence.
Rule 3: Provide a clear and comprehensive paragraph that explains what the KG describes.
Rule 4: Your response should be in one paragraph only.
[Knowledge graph triplets]
{triplets_str}
"""
    KG_description = ask_with_onlyText_retry(ask_to_LLM)
    print("\nKG description:\n", KG_description)
    return KG_description


# ---------------------------------------------------------------------------
# Phase 2: KG-Enhanced Question Pool Generation
# ---------------------------------------------------------------------------
def get_step2_ques_pool(pic_file, KG_desc, existing_ques):
    # Prompt for the LLM to generate additional information extraction aspects based on KG
    ask_to_LLM = f"""
[Task]
For a cyber threat intelligence article, I have extracted entities and relationships to construct a knowledge graph, and provided a description of the knowledge graph. Additionally, there is an image from the same article. Based on the knowledge graph description and the existing questions, please identify specific aspects of the image that can be further described, in addition to the existing questions. Please list these aspects in the form of questions. Please follow these rules in your answer:
[Rules]
Rule 1: Review the description of the knowledge graph and the existing questions provided.
Rule 2: Generate new questions that explore different perspectives or details of the image based on the information from the knowledge graph.
Rule 3: Refer to the format of the given questions, which follows the pattern: "What is/are the XXX of/in the image?", "Where XXX should be replaced with a specific aspect of the image?".
Rule 4: Make a list of the following existing questions in your answers first and then add new ones one by one.
Rule 5: Each question must begin and end with double quotation marks ("), If quotation marks are used inside the question, they must be single quotation marks (').
Rule 6: Give only one list of questions in plain text format (ensure there are no other characters such as zCode block markers) in your answer with the format: ["What is the main content of the image?", "What is the possible source of the image?", "What role does 'TrailBlazer' infrastructure play in the context of this image?", ......], and nothing else.
Rule 7: Your response can contain only one list.
[Existing questions]
{existing_ques}
[Description of knowledge graph]
{KG_desc}
"""
    step2_ques_pool = ask_with_imgANDtext_retry(pic_file, ask_to_LLM)
    start_index = step2_ques_pool.find('[')
    end_index = step2_ques_pool.rfind(']')
    if start_index != -1 and end_index != -1 and end_index > start_index:
        print("\nPhase 2 question pool:\n", step2_ques_pool[start_index:end_index + 1])
        return step2_ques_pool[start_index:end_index + 1]
    else:
        return "Please retry"


# Quote escaping helper for LLM output parsing
def custom_replace_quotes(s):
    s = s.replace('\n', '').replace('\r', '').replace('\t','').replace('\\','\\\\')
    # Find positions of all double quotes except the first and last
    first_quote = s.find('"')
    last_quote = s.rfind('"')
    if first_quote == -1 or last_quote == -1 or first_quote == last_quote:
        # Return original string if no or only one double quote found
        return s
    result = []
    i = 0
    while i < len(s):
        if s[i] == '"' and i != first_quote and i != last_quote:
            # Check for "," double-quote separator patterns
            if i + 4 <= len(s) and s[i:i+4] == '", "':
                result.append('", "')
                i += 4
                continue
            elif i + 4 <= len(s) and s[i:i+4] == '" ,"':
                result.append('" ,"')
                i += 4
                continue
            elif i + 3 <= len(s) and s[i:i+3] == '","':
                result.append('","')
                i += 3
                continue
            else:
                # Escape standalone double quotes
                result.append('\\"')
                i += 1
        else:
            result.append(s[i])
            i += 1
    return ''.join(result)

# Generate complete question pool for a single image
def get_all_question_pool(img_file, KG_description,pic_type):
    # Get question seeds based on image type
    ques_seed = get_ques_seed(pic_type)

    # Generate Phase 1 question pool from seeds
    step1_ques_pool = get_step1_ques_pool(img_file, ques_seed)
    while step1_ques_pool == "Please retry":
        step1_ques_pool = get_step1_ques_pool(img_file, ques_seed)
    step1_ques_pool = custom_replace_quotes(step1_ques_pool)
    # step1_ques_pool = step1_ques_pool.replace("\\", "\\\\")

    # Expand questions using KG description
    # Get existing questions (Phase 1 pool)
    existing_ques = '\n'.join(json.loads(step1_ques_pool))

    # Generate Phase 2 question pool
    step2_ques_pool = get_step2_ques_pool(img_file, KG_description, existing_ques)
    while step2_ques_pool == "Please retry":
        step2_ques_pool = get_step2_ques_pool(img_file, KG_description, existing_ques)
    step2_ques_pool = custom_replace_quotes(step2_ques_pool)
    # step2_ques_pool = step2_ques_pool.replace("\\", "\\\\")
    final_question_pool = json.loads(step2_ques_pool)
    return final_question_pool


# Process all images in a CTI report
def process_all_images_in_folder(picture_folder, KG_file, output_file):
    KG_description = get_KG_description(KG_file)
    questions_data = {"pictures": []}  # Store all images and their question pools

    # Iterate over all images
    for img_name in os.listdir(picture_folder):
        img_path = os.path.join(picture_folder, img_name)

        if img_name.endswith(('.png', '.jpg', '.jpeg', '.PNG')):  # Process image files only
            print(f"\nProcessing image: {img_name}")
            # Classify image type
            pic_type = judge_pic_type(img_path)
            if pic_type is None:
                print("Image read error, skipping")
                continue
            # Generate question pool
            ques_pool = get_all_question_pool(img_path, KG_description,pic_type)

            # Add questions for this image to results
            questions_data["pictures"].append({
                "name": img_name,
                "pic_type": pic_type,
                "questions": [{"question": q} for q in ques_pool]
            })

    # Write question data to file
    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(questions_data, outfile, indent=4, ensure_ascii=False)
    print(f"Question pool saved to {output_file}")


if __name__ == "__main__":
    picture_folder = "../dataCTI/00/picture"  # Path to the image folder
    KG_file = "../dataCTI/00/original/KG.json"  # Path to the KG file
    output_file = "../dataCTI/00/Questions.json"  # Path to the output JSON file
    # Execute the function
    process_all_images_in_folder(picture_folder, KG_file, output_file)






