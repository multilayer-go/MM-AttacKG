# -*- coding: utf-8 -*-
import json

def get_latest_answer(qa):
    """Get the most recent answer: original if no iteration, else latest iteration."""
    if not qa['iteration']:  # No iteration
        return qa['answer'],qa['question']
    else:  # Has iterations, take the last round
        return qa['iteration'][-1]['answer'],qa['question']

def process_answer_res(img_data):
    """Extract answers that meet quality criteria."""
    answer_res = []  # Store qualifying answers
    ques_res = []  # Store corresponding questions

    for qa in img_data['questionsANDanswersANDqlabelsANDmarkANDiteration']:
        question = qa['question']
        latest_answer,latest_ques = get_latest_answer(qa)

        # If qlabel is "yes", include the latest answer directly
        if qa['qlabel'] == 'yes':
            answer_res.append(latest_answer)
            ques_res.append(latest_ques)

        # If qlabel is "no", check mark and include if "excellent"
        if qa['qlabel'] == 'no':
            # No iteration: check original mark
            if not qa['iteration'] and qa['mark'] == 'excellent':
                answer_res.append(latest_answer)
                ques_res.append(latest_ques)
            # Has iterations: check latest mark
            elif qa['iteration'] and qa['iteration'][-1]['mark'] == 'excellent':
                answer_res.append(latest_answer)
                ques_res.append(latest_ques)

    return answer_res,ques_res

def main_extract(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile:
        data = json.load(infile)

    result = {
        "pictures": [],
        "AllanswerRes": []
    }

    # Iterate over each image
    for picture in data['pictures']:
        img_name = picture['name']
        img_data = picture  # Image data containing questions, answers, qlabel, etc.
        print(f"\nProcessing qualifying answers for image {img_name}")

        # Get qualifying answers
        answer_res,ques_res = process_answer_res(img_data)

        # Save results
        result["pictures"].append({
            'name': img_name,
            'questionRes':ques_res,
            'answerRes': answer_res
        })

        # Add qualifying answers to AllanswerRes
        result["AllanswerRes"].extend(answer_res)

    # Write results to output file
    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(result, outfile, indent=4, ensure_ascii=False)

    print(f"Qualifying answers saved to {output_file}")


# Call the main function
if __name__ == "__main__":
    input_file = "../dataCTI/00/Iteration_Form2.json"
    output_file = "../dataCTI/00/answerRes.json"  # Output file path (answerRes.json)

    main_extract(input_file, output_file)












