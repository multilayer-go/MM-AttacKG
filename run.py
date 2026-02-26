#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MM-AttacKG Main Entry Point

Provides a unified command-line interface for the knowledge graph construction pipeline.

Usage:
    # Process a single CTI report
    python run.py single --cti-id 00
    
    # Process a single CTI report (specify step range)
    python run.py single --cti-id 00 --steps 1-3
    
    # Batch process all CTI reports
    python run.py batch
    
    # Batch process specific CTI reports
    python run.py batch --cti-ids 00 01 02
"""

import argparse
import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pipeline.step1_question_generation import process_all_images_in_folder
from pipeline.step2_answer_generation import process_answers_from_questions
from pipeline.step3_theme_judging import process_labels_from_answers
from pipeline.step4_marking import process_marks_from_labels
from pipeline.step5_iteration_form1 import main_form1
from pipeline.step5_iteration_form2 import main_form2
from pipeline.step6_extraction import main_extract


class Pipeline:
    """Knowledge Graph Construction Pipeline."""
    
    def __init__(self, cti_id, base_path="data/cti_reports"):
        self.cti_id = cti_id
        self.base_path = Path(base_path)
        self.cti_path = self.base_path / cti_id
        self._setup_paths()
    
    def _setup_paths(self):
        """Set up all file paths."""
        self.picture_folder = self.cti_path / "picture"
        self.kg_file = self.cti_path / "original" / "KG.json"
        self.process_folder = self.cti_path / "process"
        
        # Create processing directory
        self.process_folder.mkdir(parents=True, exist_ok=True)
        
        # Output files for each step
        self.files = {
            'step1_output': self.process_folder / "JSONstep1_Questions.json",
            'step2_input': self.process_folder / "JSONstep1_Questions.json",
            'step2_output': self.process_folder / "JSONstep2_Answers.json",
            'step3_input': self.process_folder / "JSONstep2_Answers.json",
            'step3_output': self.process_folder / "JSONstep3_QLabels.json",
            'step4_input': self.process_folder / "JSONstep3_QLabels.json",
            'step4_output': self.process_folder / "JSONstep4_Mark.json",
            'step5_input': self.process_folder / "JSONstep4_Mark.json",
            'step5_form1_output': self.process_folder / "JSONstep5_Iteration_Form1.json",
            'step5_form2_output': self.process_folder / "JSONstep5_Iteration_Form2.json",
            'step6_input': self.process_folder / "JSONstep5_Iteration_Form2.json",
            'step6_output': self.process_folder / "JSONstep6_answerRes.json",
        }
    
    def step1_question_generation(self):
        """Step 1: Question Generation."""
        print(f"\n{'='*60}")
        print(f"CTI {self.cti_id} - Step 1: Question Generation")
        print(f"{'='*60}")
        process_all_images_in_folder(
            str(self.picture_folder),
            str(self.kg_file),
            str(self.files['step1_output'])
        )
        print(f"✓ Questions saved to: {self.files['step1_output']}")
    
    def step2_answer_generation(self):
        """Step 2: Answer Generation."""
        print(f"\n{'='*60}")
        print(f"CTI {self.cti_id} - Step 2: Answer Generation")
        print(f"{'='*60}")
        process_answers_from_questions(
            str(self.files['step2_input']),
            str(self.files['step2_output']),
            str(self.picture_folder)
        )
        print(f"✓ Answers saved to: {self.files['step2_output']}")
    
    def step3_theme_judging(self):
        """Step 3: Theme Judging."""
        print(f"\n{'='*60}")
        print(f"CTI {self.cti_id} - Step 3: Theme Judging")
        print(f"{'='*60}")
        process_labels_from_answers(
            str(self.files['step3_input']),
            str(self.files['step3_output'])
        )
        print(f"✓ Labels saved to: {self.files['step3_output']}")
    
    def step4_marking(self):
        """Step 4: Answer Marking."""
        print(f"\n{'='*60}")
        print(f"CTI {self.cti_id} - Step 4: Answer Marking")
        print(f"{'='*60}")
        process_marks_from_labels(
            str(self.files['step4_input']),
            str(self.files['step4_output']),
            str(self.picture_folder)
        )
        print(f"✓ Marks saved to: {self.files['step4_output']}")
    
    def step5_iteration(self, form=2):
        """Step 5: Iterative Refinement."""
        print(f"\n{'='*60}")
        print(f"CTI {self.cti_id} - Step 5: Iteration (Form {form})")
        print(f"{'='*60}")
        
        if form == 1:
            main_form1(
                str(self.files['step5_input']),
                str(self.files['step5_form1_output']),
                str(self.picture_folder)
            )
            print(f"✓ Iteration results saved to: {self.files['step5_form1_output']}")
        else:
            main_form2(
                str(self.files['step5_input']),
                str(self.files['step5_form2_output']),
                str(self.picture_folder)
            )
            print(f"✓ Iteration results saved to: {self.files['step5_form2_output']}")
    
    def step6_extraction(self):
        """Step 6: Answer Extraction."""
        print(f"\n{'='*60}")
        print(f"CTI {self.cti_id} - Step 6: Answer Extraction")
        print(f"{'='*60}")
        main_extract(
            str(self.files['step6_input']),
            str(self.files['step6_output'])
        )
        print(f"✓ Final results saved to: {self.files['step6_output']}")
    
    def run_steps(self, start_step=1, end_step=6):
        """Run specified range of steps."""
        steps = {
            1: self.step1_question_generation,
            2: self.step2_answer_generation,
            3: self.step3_theme_judging,
            4: self.step4_marking,
            5: self.step5_iteration,
            6: self.step6_extraction,
        }
        
        print(f"\n{'#'*60}")
        print(f"# Processing CTI Report: {self.cti_id}")
        print(f"# Steps: {start_step} to {end_step}")
        print(f"{'#'*60}")
        
        for step_num in range(start_step, end_step + 1):
            if step_num in steps:
                try:
                    steps[step_num]()
                except Exception as e:
                    print(f"\n❌ Error in Step {step_num}: {e}")
                    raise
        
        print(f"\n{'#'*60}")
        print(f"# ✓ CTI {self.cti_id} Processing Complete!")
        print(f"{'#'*60}\n")


def run_single_cti(cti_id, steps=None):
    """Process a single CTI report."""
    if steps:
        start, end = map(int, steps.split('-'))
    else:
        start, end = 1, 6
    
    pipeline = Pipeline(cti_id)
    pipeline.run_steps(start, end)


def run_batch_cti(cti_ids=None, steps=None):
    """Batch process CTI reports."""
    base_path = Path("data/cti_reports")
    
    if cti_ids is None:
        # Get all CTI IDs
        cti_ids = [f.name for f in base_path.iterdir() if f.is_dir() and f.name.isdigit()]
        cti_ids.sort()
    
    print(f"\n{'#'*60}")
    print(f"# Batch Processing {len(cti_ids)} CTI Reports")
    print(f"# CTI IDs: {', '.join(cti_ids)}")
    print(f"{'#'*60}\n")
    
    for cti_id in cti_ids:
        try:
            run_single_cti(cti_id, steps)
        except Exception as e:
            print(f"\n❌ Failed to process CTI {cti_id}: {e}")
            continue


def main():
    parser = argparse.ArgumentParser(
        description="MM-AttacKG: Multimodal Attack Knowledge Graph Construction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single CTI report
  python run.py single --cti-id 00
  
  # Process a single CTI report (steps 1-3 only)
  python run.py single --cti-id 00 --steps 1-3
  
  # Batch process all CTI reports
  python run.py batch
  
  # Batch process specific CTI reports
  python run.py batch --cti-ids 00 01 02
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # 'single' command
    single_parser = subparsers.add_parser('single', help='Process a single CTI report')
    single_parser.add_argument('--cti-id', required=True, help='CTI report ID (e.g., 00, 01, 02)')
    single_parser.add_argument('--steps', help='Step range (e.g., 1-3, 1-6)')
    
    # 'batch' command
    batch_parser = subparsers.add_parser('batch', help='Process multiple CTI reports')
    batch_parser.add_argument('--cti-ids', nargs='+', help='Specific CTI IDs to process')
    batch_parser.add_argument('--steps', help='Step range (e.g., 1-3, 1-6)')
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'single':
            run_single_cti(args.cti_id, args.steps)
        elif args.command == 'batch':
            run_batch_cti(args.cti_ids, args.steps)
    except KeyboardInterrupt:
        print("\n\n⚠ Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
