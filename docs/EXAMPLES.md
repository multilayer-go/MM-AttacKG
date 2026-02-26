# Usage Examples

This document provides practical examples for using MM-AttacKG.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Configuration Examples](#configuration-examples)
3. [Processing Single CTI](#processing-single-cti)
4. [Batch Processing](#batch-processing)
5. [Advanced Usage](#advanced-usage)
6. [Integration Examples](#integration-examples)

---

## Basic Usage

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/MM-AttacKG.git
cd MM-AttacKG

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .
```

### Configuration

```bash
# Copy example configuration
cp config/config.example.yaml config/config.yaml

# Edit configuration
nano config/config.yaml  # or use your favorite editor

# Set API keys
export DASHSCOPE_API_KEY="your-key"
```

---

## Configuration Examples

### Minimal Configuration

```yaml
# config/config.yaml
api:
  dashscope:
    api_key: "your-dashscope-key"

paths:
  data_root: "data/cti_reports"
```

### Full Configuration

```yaml
# config/config.yaml
api:
  dashscope:
    api_key: "sk-xxx"
    model: "qwen-max"
  eval:
    api_key: "sk-xxx"  # defaults to dashscope key
    model: "qwen2.5-72b-instruct"

processing:
  max_retries: 5
  timeout: 120
  temperature: 0
  max_workers: 5

pipeline:
  question_generation:
    enabled: true
  answer_generation:
    enabled: true
  theme_judging:
    enabled: true
    filter_mode: "both"
  marking:
    enabled: true
  iteration:
    enabled: true
    form: 2
    max_rounds: 3
  extraction:
    enabled: true

logging:
  level: "INFO"
  file: "logs/mm-attackg.log"
```

### Environment Variables

```bash
# .env
DASHSCOPE_API_KEY=sk-xxx
LOG_LEVEL=DEBUG
```

---

## Processing Single CTI

### Example 1: Process Specific CTI Report

```bash
# Process CTI report 00
python src/run_single_cti.py --cti-id 00

# Or using installed command
mm-attackg-single --cti-id 00
```

### Example 2: Run Specific Steps

```bash
# Run only step 1 (question generation)
python src/run_single_cti.py --cti-id 00 --steps 1

# Run steps 1-3
python src/run_single_cti.py --cti-id 00 --steps 1,2,3

# Run steps 4-6
python src/run_single_cti.py --cti-id 00 --steps 4,5,7
```

### Example 3: Custom Configuration

```bash
# Use custom config file
python src/run_single_cti.py --cti-id 00 --config my_config.yaml

# Use specific iteration form
python src/run_single_cti.py --cti-id 00 --iteration-form 1

# Disable iteration
python src/run_single_cti.py --cti-id 00 --no-iteration
```

---

## Batch Processing

### Example 1: Process All CTI Reports

```bash
# Process all CTI reports
python src/run_all_cti.py

# Or using installed command
mm-attackg-batch
```

### Example 2: Process Range of Reports

```bash
# Process CTI reports 00-05
python src/run_all_cti.py --start 00 --end 05

# Process from CTI 10 onwards
python src/run_all_cti.py --start 10
```

### Example 3: Resume Processing

```bash
# Resume from last checkpoint
python src/run_all_cti.py --resume

# Skip already processed
python src/run_all_cti.py --skip-existing
```

---

## Advanced Usage

### Example 1: Python API Usage

```python
from src.pipeline.step1_question_generation import process_all_images_in_folder
from src.pipeline.step2_answer_generation import process_answers_from_questions
from src.utils.config_loader import get_config

# Load configuration
config = get_config()

# Process images
picture_folder = "data/cti_reports/00/picture"
kg_file = "data/cti_reports/00/original/KG.json"
output_file = "data/cti_reports/00/process/questions.json"

process_all_images_in_folder(picture_folder, kg_file, output_file)

# Generate answers
input_file = "data/cti_reports/00/process/questions.json"
output_file = "data/cti_reports/00/process/answers.json"

process_answers_from_questions(input_file, output_file, picture_folder)
```

### Example 2: Custom Pipeline

```python
from src.pipeline import (
    step1_question_generation,
    step2_answer_generation,
    step3_theme_judging,
    step6_extraction
)

# Custom pipeline without marking and iteration
def custom_pipeline(cti_id):
    base_path = f"data/cti_reports/{cti_id}"
    
    # Step 1: Questions
    step1_question_generation.process_all_images_in_folder(
        f"{base_path}/picture",
        f"{base_path}/original/KG.json",
        f"{base_path}/process/step1.json"
    )
    
    # Step 2: Answers
    step2_answer_generation.process_answers_from_questions(
        f"{base_path}/process/step1.json",
        f"{base_path}/process/step2.json",
        f"{base_path}/picture"
    )
    
    # Step 3: Filtering
    step3_theme_judging.process_labels_from_answers(
        f"{base_path}/process/step2.json",
        f"{base_path}/process/step3.json",
        f"{base_path}/picture"
    )
    
    # Step 6: Extraction (using step3 output directly)
    step6_extraction.main_extract(
        f"{base_path}/process/step3.json",
        f"{base_path}/process/final.json"
    )

# Run custom pipeline
custom_pipeline("00")
```

### Example 3: Custom Image Classification

```python
from src.pipeline.step1_question_generation import judge_pic_type, get_ques_seed

# Classify image
image_path = "data/cti_reports/00/picture/attack_flow.png"
image_type = judge_pic_type(image_path)
print(f"Image type: {image_type}")

# Get question seeds for type
question_seeds = get_ques_seed(image_type)
print(f"Question seeds: {question_seeds}")
```

### Example 4: Direct API Usage

```python
from src.utils.api_connector import ask_with_imgANDtext_retry
from src.utils.config_loader import get_config

# Load config
config = get_config()

# Ask question about image
image_path = "data/cti_reports/00/picture/malware_code.png"
question = "What malware family does this code belong to?"

response = ask_with_imgANDtext_retry(
    image_path,
    question,
    max_retries=3
)

print(f"Answer: {response}")
```

---

## Integration Examples

### Example 1: Integration with Jupyter Notebook

```python
# notebook.ipynb
import sys
sys.path.append('..')

from src.pipeline.step1_question_generation import process_all_images_in_folder
from src.utils.config_loader import get_config
import json

# Process and display results
config = get_config('../config/config.yaml')
process_all_images_in_folder(
    "../data/cti_reports/00/picture",
    "../data/cti_reports/00/original/KG.json",
    "../data/cti_reports/00/process/questions.json"
)

# Load and display
with open("../data/cti_reports/00/process/questions.json") as f:
    data = json.load(f)
    
for pic in data['pictures']:
    print(f"\n{pic['name']}:")
    for q in pic['finalQuesPool']:
        print(f"  - {q}")
```

### Example 2: Integration with Flask API

```python
# api.py
from flask import Flask, request, jsonify
from src.pipeline.step2_answer_generation import process_answers_from_questions
from src.utils.config_loader import get_config
import tempfile
import json

app = Flask(__name__)
config = get_config()

@app.route('/process_image', methods=['POST'])
def process_image():
    """API endpoint to process uploaded image."""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    image = request.files['image']
    questions = request.json.get('questions', [])
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        image.save(tmp.name)
        
        # Process
        # ... processing logic ...
        
        return jsonify({
            'status': 'success',
            'answers': []  # processed answers
        })

if __name__ == '__main__':
    app.run(debug=True)
```

### Example 3: Integration with Database

```python
# database_integration.py
import sqlite3
from src.pipeline.step6_extraction import main_extract
import json

def save_to_database(cti_id):
    """Save processed results to SQLite database."""
    
    # Extract answers
    input_file = f"data/cti_reports/{cti_id}/process/step5_iteration_form2.json"
    output_file = f"data/cti_reports/{cti_id}/process/step6_final.json"
    main_extract(input_file, output_file)
    
    # Load results
    with open(output_file) as f:
        data = json.load(f)
    
    # Save to database
    conn = sqlite3.connect('mm_attackg.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY,
            cti_id TEXT,
            image_name TEXT,
            question TEXT,
            answer TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    for pic in data['pictures']:
        for q, a in zip(pic['questionRes'], pic['answerRes']):
            cursor.execute(
                'INSERT INTO answers (cti_id, image_name, question, answer) VALUES (?, ?, ?, ?)',
                (cti_id, pic['name'], q, a)
            )
    
    conn.commit()
    conn.close()

# Usage
save_to_database("00")
```

---

## Common Use Cases

### Use Case 1: Quick Analysis of Single Image

```python
from src.utils.api_connector import ask_with_imgANDtext_retry

# Quick question about image
image = "data/cti_reports/00/picture/attack_diagram.png"
question = "What attack techniques are shown in this diagram?"

answer = ask_with_imgANDtext_retry(image, question)
print(answer)
```

### Use Case 2: Bulk Processing with Progress

```python
from tqdm import tqdm
from src.pipeline.step2_answer_generation import process_answers_from_questions

# Process multiple CTI reports with progress bar
cti_ids = ["00", "01", "02", "03", "04"]

for cti_id in tqdm(cti_ids, desc="Processing CTI reports"):
    try:
        input_file = f"data/cti_reports/{cti_id}/process/step1.json"
        output_file = f"data/cti_reports/{cti_id}/process/step2.json"
        picture_folder = f"data/cti_reports/{cti_id}/picture"
        
        process_answers_from_questions(input_file, output_file, picture_folder)
        print(f"✓ Processed {cti_id}")
    except Exception as e:
        print(f"✗ Error processing {cti_id}: {e}")
```

### Use Case 3: Quality Analysis

```python
import json
from collections import Counter

def analyze_quality(cti_id):
    """Analyze answer quality distribution."""
    
    with open(f"data/cti_reports/{cti_id}/process/step4_marks.json") as f:
        data = json.load(f)
    
    marks = []
    for pic in data['pictures']:
        for qa in pic['questionsANDanswersANDqlabelsANDmark']:
            marks.append(qa.get('mark', 'unknown'))
    
    quality_dist = Counter(marks)
    
    print(f"Quality Distribution for CTI {cti_id}:")
    for quality, count in quality_dist.items():
        print(f"  {quality}: {count}")
    
    return quality_dist

# Analyze
analyze_quality("00")
```

---

## Troubleshooting Examples

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python src/run_single_cti.py --cti-id 00
```

### Test API Connection

```python
from src.utils.api_connector import ask_with_onlyText_retry

try:
    response = ask_with_onlyText_retry("Hello, are you working?")
    print(f"API is working: {response}")
except Exception as e:
    print(f"API connection failed: {e}")
```

### Verify Configuration

```python
from src.utils.config_loader import get_config

config = get_config()

# Check API keys
dashscope_key = config.get('api.dashscope.api_key')

print(f"DashScope API Key: {dashscope_key[:10]}..." if dashscope_key else "Not configured")
```

---

## Performance Optimization

### Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor
from src.pipeline.step2_answer_generation import process_answers_from_questions

def process_cti_parallel(cti_ids):
    """Process multiple CTI reports in parallel."""
    
    def process_one(cti_id):
        input_file = f"data/cti_reports/{cti_id}/process/step1.json"
        output_file = f"data/cti_reports/{cti_id}/process/step2.json"
        picture_folder = f"data/cti_reports/{cti_id}/picture"
        
        process_answers_from_questions(input_file, output_file, picture_folder)
        return cti_id
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(process_one, cti_ids))
    
    return results

# Process CTI 00-05 in parallel
process_cti_parallel(["00", "01", "02", "03", "04", "05"])
```

---

For more examples and detailed documentation, see:
- [Pipeline Architecture](PIPELINE.md)
- [API Documentation](API.md)
- [Project README](../README.md)
