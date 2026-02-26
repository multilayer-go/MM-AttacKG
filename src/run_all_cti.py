# -*- coding: utf-8 -*-
"""
Batch CTI Reports Processor

This script processes multiple CTI reports through the complete pipeline.

Usage:
    python run_all_cti.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import pytz

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from pipeline.step1_question_generation import process_all_images_in_folder
from pipeline.step2_answer_generation import process_answers_from_questions
from pipeline.step3_theme_judging import process_labels_from_answers
from pipeline.step4_marking import process_marks_from_labels
from pipeline.step5_iteration_form1 import main_form1
from pipeline.step5_iteration_form2 import main_form2
from pipeline.step6_extraction import main_extract


def get_all_folders_in_dataCTI(data_cti_path):
    """Get all subdirectory names under data/cti_reports (e.g., 00, 01, 02, ...)."""
    return sorted([f for f in os.listdir(data_cti_path)
                   if os.path.isdir(os.path.join(data_cti_path, f))])


def get_file_path(num, data_cti_path):
    """Build all input/output file paths for a given CTI report ID."""
    picture_folder = os.path.join(data_cti_path, num, "picture")
    KG_file = os.path.join(data_cti_path, num, "original", "KG.json")

    process_folder = os.path.join(data_cti_path, num, "process")
    if not os.path.exists(process_folder):
        os.makedirs(process_folder)

    output_file_step1 = os.path.join(process_folder, "JSONstep1_Questions.json")
    input_file_step2 = os.path.join(process_folder, "JSONstep1_Questions.json")
    output_file_step2 = os.path.join(process_folder, "JSONstep2_Answers.json")
    input_file_step3 = os.path.join(process_folder, "JSONstep2_Answers.json")
    output_file_step3 = os.path.join(process_folder, "JSONstep3_QLabels.json")
    input_file_step4 = os.path.join(process_folder, "JSONstep3_QLabels.json")
    output_file_step4 = os.path.join(process_folder, "JSONstep4_Mark.json")
    input_file_step5 = os.path.join(process_folder, "JSONstep4_Mark.json")
    output_file_step5_Form1 = os.path.join(process_folder, "JSONstep5_Iteration_Form1.json")
    output_file_step5_Form2 = os.path.join(process_folder, "JSONstep5_Iteration_Form2.json")
    input_file_step6 = os.path.join(process_folder, "JSONstep5_Iteration_Form2.json")
    output_file_step6 = os.path.join(process_folder, "JSONstep6_answerRes.json")

    return (picture_folder, KG_file,
            output_file_step1, input_file_step2, output_file_step2,
            input_file_step3, output_file_step3,
            input_file_step4, output_file_step4,
            input_file_step5, output_file_step5_Form1, output_file_step5_Form2,
            input_file_step6, output_file_step6)


if __name__ == "__main__":
    root_dir = Path(__file__).parent.parent
    data_cti_path = str(root_dir / "data" / "cti_reports")
    all_folders = get_all_folders_in_dataCTI(data_cti_path)

    for folder in all_folders:
        print(f"\n\nProcessing folder: {folder}\n")

        (picture_folder, KG_file,
         output_file_step1, input_file_step2, output_file_step2,
         input_file_step3, output_file_step3,
         input_file_step4, output_file_step4,
         input_file_step5, output_file_step5_Form1, output_file_step5_Form2,
         input_file_step6, output_file_step6) = get_file_path(folder, data_cti_path)

        # Step 1: Question Generation
        print(f"--------------------------------------------------Folder:{folder} STEP 1--------------------------------------------------")
        process_all_images_in_folder(picture_folder, KG_file, output_file_step1)

        # Step 2: Answer Generation
        print(f"--------------------------------------------------Folder:{folder} STEP 2--------------------------------------------------")
        process_answers_from_questions(input_file_step2, output_file_step2, picture_folder)

        # Step 3: Theme Judging
        print(f"--------------------------------------------------Folder:{folder} STEP 3--------------------------------------------------")
        process_labels_from_answers(input_file_step3, output_file_step3, picture_folder)

        # Step 4: Answer Marking
        print(f"--------------------------------------------------Folder:{folder} STEP 4--------------------------------------------------")
        process_marks_from_labels(input_file_step4, output_file_step4, picture_folder)

        # Step 5: Iterative Refinement
        print(f"--------------------------------------------------Folder:{folder} STEP 5--------------------------------------------------")
        main_form2(input_file_step5, output_file_step5_Form2, picture_folder)
        main_form1(input_file_step5, output_file_step5_Form1, picture_folder)

        # Step 6: Answer Extraction
        print(f"--------------------------------------------------Folder:{folder} STEP 6--------------------------------------------------")
        main_extract(input_file_step6, output_file_step6)

    cn_tz = pytz.timezone('Asia/Shanghai')
    print("Finished at:", datetime.now(cn_tz).strftime('%Y-%m-%d %H:%M:%S'))





