# MM-AttacKG

**Multimodal Attack Knowledge Graph Construction from CTI Reports**

[中文版 README](README_CN.md)

---

## Overview

MM-AttacKG is a multimodal pipeline that automatically constructs attack knowledge graphs from Cyber Threat Intelligence (CTI) reports. It leverages large language models (LLMs) with both text and vision capabilities to extract structured security entities, relationships, and MITRE ATT&CK technique mappings from reports containing text and images (e.g., screenshots, diagrams, flowcharts).

### Key Features

- **Multimodal Analysis**: Processes both images (screenshots, network diagrams, decompiled code, etc.) and textual content from CTI reports.
- **6-Step Pipeline**: Systematic extraction through question generation, answer generation, theme judging, answer marking, iterative refinement, and final extraction.
- **MITRE ATT&CK Mapping**: Automatically maps extracted attack behaviors to MITRE ATT&CK tactics and techniques.
- **Domestic LLM Architecture**: Fully based on DashScope (Qwen) series models from Alibaba Cloud for both primary analysis and independent answer evaluation. The system provides an extensible evaluation interface that supports third-party LLMs, but due to service access restrictions, only domestic models were used in practice.
- **Robust Execution**: Built-in retry logic, timeout handling, and exponential backoff for reliable API interactions.

---

## Architecture

```
CTI Report (images + text)
        │
        ▼
┌─────────────────────────────────────────────┐
│  Step 1: Question Generation                │  Generate questions for each image
│  Step 2: Answer Generation                  │  Answer questions using multimodal LLM
│  Step 3: Theme Judging                      │  Classify relevance to security themes
│  Step 4: Answer Marking                     │  Evaluate answer quality (Qwen)
│  Step 5: Iterative Refinement               │  Improve low-quality answers
│  Step 6: Answer Extraction                  │  Extract structured entities
└─────────────────────────────────────────────┘
        │
        ▼
  Attack Knowledge Graph (JSON)
```

---

## Quick Start

### 1. Prerequisites

- Python 3.8+
- DashScope API key (for Qwen models)
- DashScope API key (for Qwen evaluation model)

### 2. Installation

```bash
git clone https://github.com/yourusername/MM-AttacKG.git
cd MM-AttacKG
pip install -r requirements.txt
```

### 3. Configuration

Set the following environment variables (or create a `.env` file):

```bash
# Required: DashScope (Qwen) API
export DASHSCOPE_API_KEY="your-dashscope-api-key"
export DASHSCOPE_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"  # optional
export TEXT_MODEL="qwen2.5-72b-instruct"    # optional, default
export VISION_MODEL="qwen2.5-vl-72b-instruct"  # optional, default

# Optional: Evaluation model configuration (for Step 4 answer marking)
# By default uses DashScope API with the same key as above
# export EVAL_API_KEY="your-dashscope-api-key"    # defaults to DASHSCOPE_API_KEY
# export EVAL_API_URL="https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
# export EVAL_MODEL="qwen2.5-72b-instruct"
```

Or copy and edit the example config:

```bash
cp config/config.example.yaml config/config.yaml
# Edit config.yaml with your API keys
```

### 4. Prepare Data

Place your CTI report data under `data/cti_reports/<ID>/`:

```
data/cti_reports/00/
├── original/
│   ├── KG.json          # Ground truth knowledge graph (for evaluation)
│   ├── outline.json     # Report outline / structured text
│   └── In-context.json  # In-context learning examples
├── picture/             # Report images (screenshots, diagrams, etc.)
│   ├── image1.png
│   ├── image2.png
│   └── ...
└── process/             # Pipeline output (auto-generated)
```

### 5. Run

```bash
# Process a single CTI report
python run.py single --cti-id 00

# Process specific pipeline steps only
python run.py single --cti-id 00 --steps 1-3

# Batch process all CTI reports
python run.py batch

# Batch process specific reports
python run.py batch --cti-ids 00 01 02
```

---

## Pipeline Steps

| Step | Name | Description | Model |
|------|------|-------------|-------|
| 1 | Question Generation | Generates structured questions for each image based on report outline and MITRE framework | Qwen (text) |
| 2 | Answer Generation | Answers questions using multimodal LLM with image + text context | Qwen (vision) |
| 3 | Theme Judging | Classifies each Q&A pair's relevance to predefined security themes | Qwen (vision) |
| 4 | Answer Marking | Independent evaluation of answer quality using a separate LLM | Qwen (text) |
| 5 | Iterative Refinement | Re-generates answers for low-scoring items with improvement suggestions | Qwen (vision) |
| 6 | Answer Extraction | Extracts final structured entities and attack knowledge from refined answers | Qwen (text) |

---

## Image Categories

The pipeline recognizes and processes 6 types of images commonly found in CTI reports:

| Category | Description |
|----------|-------------|
| `code_screenshot` | Screenshots of code, scripts, or command-line output |
| `network_diagram` | Network topology diagrams and communication flow charts |
| `decompiled_code` | Decompiled or disassembled code from malware analysis |
| `attack_flow` | Attack process flowcharts and kill chain diagrams |
| `system_screenshot` | System interface screenshots, configuration panels |
| `data_table` | Tables, charts, and statistical data visualizations |

---

## Project Structure

```
MM-AttacKG/
├── run.py                          # Main CLI entry point
├── config/
│   └── config.example.yaml         # Example configuration
├── data/
│   ├── cti_reports/                # CTI report data
│   │   ├── 00/ ... 11/            # Individual report folders
│   └── resources/                  # Shared resources
│       ├── entity_types.json       # Entity type definitions
│       ├── mitre_framework.json    # MITRE ATT&CK framework
│       └── mitre_tactics_techniques.json
├── src/
│   ├── pipeline/                   # 6-step pipeline modules
│   │   ├── step1_question_generation.py
│   │   ├── step2_answer_generation.py
│   │   ├── step3_theme_judging.py
│   │   ├── step4_marking.py
│   │   ├── step5_iteration_form1.py
│   │   ├── step5_iteration_form2.py
│   │   └── step6_extraction.py
│   ├── utils/                      # Utility modules
│   │   ├── api_connector.py        # LLM API interface
│   │   ├── config_loader.py        # Configuration loader
│   │   └── logger.py               # Logging utilities
│   ├── run_single_cti.py           # Single CTI processor
│   └── run_all_cti.py              # Batch CTI processor
├── docs/                           # Documentation
├── requirements.txt
├── setup.py
└── LICENSE
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DASHSCOPE_API_KEY` | Yes | — | DashScope API key for Qwen models |
| `DASHSCOPE_BASE_URL` | No | `https://dashscope.aliyuncs.com/compatible-mode/v1` | DashScope API base URL |
| `TEXT_MODEL` | No | `qwen2.5-72b-instruct` | Text-only LLM model name |
| `VISION_MODEL` | No | `qwen2.5-vl-72b-instruct` | Vision LLM model name |
| `EVAL_API_KEY` | No | Same as `DASHSCOPE_API_KEY` | API key for Step 4 evaluation model |
| `EVAL_API_URL` | No | `https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions` | Evaluation API endpoint |
| `EVAL_MODEL` | No | `qwen2.5-72b-instruct` | Evaluation model name |

---

## Output Format

The pipeline produces a JSON file for each step. The final output (`JSONstep6_answerRes.json`) contains structured attack knowledge:

```json
[
  {
    "image": "image1.png",
    "category": "network_diagram",
    "entities": [
      {
        "entity": "C2 Server",
        "type": "infrastructure",
        "attributes": { ... }
      }
    ],
    "tactics": ["Command and Control"],
    "techniques": ["T1071 - Application Layer Protocol"]
  }
]
```

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- [MITRE ATT&CK](https://attack.mitre.org/) for the threat intelligence framework
- [Alibaba Cloud DashScope](https://dashscope.aliyun.com/) for Qwen model APIs
