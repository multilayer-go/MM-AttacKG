# Pipeline Architecture

This document provides detailed information about the MM-AttacKG processing pipeline.

## Overview

The MM-AttacKG pipeline processes cyber threat intelligence (CTI) report images through a series of steps to extract structured knowledge. The pipeline is designed to be modular, allowing individual steps to be executed independently or as a complete workflow.

## Pipeline Steps

### Step 1: Question Generation

**Module**: `src/pipeline/step1_question_generation.py`

**Purpose**: Generate relevant questions based on image content type.

**Process**:
1. Classify image into one of 7 categories
2. Select appropriate question seeds for the category
3. Generate initial question pool
4. Expand questions using LLM with image context

**Input**:
- Image file
- KG.json (existing knowledge graph data)

**Output**:
- `JSONstep1_Questions.json`: List of generated questions per image

**Configuration**:
```yaml
pipeline:
  question_generation:
    enabled: true
    expand_questions: true
```

### Step 2: Answer Generation

**Module**: `src/pipeline/step2_answer_generation.py`

**Purpose**: Generate answers to questions using multimodal understanding.

**Process**:
1. Load questions from Step 1
2. For each question:
   - Retrieve image context
   - Retrieve CTI outline
   - Query multimodal LLM with image + context
3. Multi-threaded processing for efficiency

**Input**:
- `JSONstep1_Questions.json`
- Images
- `in_context.json`: Image context in CTI report
- `outline.json`: CTI report summary

**Output**:
- `JSONstep2_Answers.json`: Questions with initial answers

**Key Features**:
- Parallel processing with thread pool
- Combines image, in-context, and CTI summary
- Structured answer format

### Step 3: Theme Judging

**Module**: `src/pipeline/step3_theme_judging.py`

**Purpose**: Filter questions and answers for cybersecurity relevance.

**Process**:
1. **First Pass**: Judge questions independently
   - Determine if question is relevant to cybersecurity
   - Mark with "pertinent" or "irrelevant"

2. **Second Pass**: Judge question-answer pairs
   - For questions marked irrelevant, re-evaluate with answer
   - More accurate filtering using complete context

**Input**:
- `JSONstep2_Answers.json`

**Output**:
- `JSONstep3_QLabels.json`: Questions with relevance labels

**Configuration**:
```yaml
pipeline:
  theme_judging:
    enabled: true
    filter_mode: "both"  # question_only, qa_pair, or both
```

### Step 4: Answer Marking

**Module**: `src/pipeline/step4_marking.py`

**Purpose**: Evaluate answer quality using an independent LLM (Qwen).

**Process**:
1. For each question-answer pair:
   - Present image and Q&A to the evaluation model
   - Request quality evaluation
   - Assign mark: "excellent", "good", or "poor"
2. Retry mechanism for API failures
3. Greeting response detection and retry

**Input**:
- `JSONstep3_QLabels.json`
- Images

**Output**:
- `JSONstep4_Mark.json`: Answers with quality marks

**Marking Criteria**:
- **Excellent**: Accurate, complete, directly addresses question
- **Good**: Mostly accurate but may lack detail
- **Poor**: Inaccurate, incomplete, or off-topic

### Step 5: Iterative Refinement

**Modules**: 
- `src/pipeline/step5_iteration_form1.py` (without suggestions)
- `src/pipeline/step5_iteration_form2.py` (with suggestions)

**Purpose**: Improve low-quality answers through iteration.

**Form 1 Process** (No Suggestions):
1. Identify answers marked as "good" or "poor"
2. Re-query LLM with refined prompt
3. Update answer and re-mark quality
4. Repeat up to max rounds or until quality threshold met

**Form 2 Process** (With Suggestions):
1. Same as Form 1, but include improvement suggestions
2. LLM receives feedback on what to improve
3. More directed refinement

**Input**:
- `JSONstep4_Mark.json`
- Images

**Output**:
- `JSONstep5_Iteration_Form1.json` or `JSONstep5_Iteration_Form2.json`

**Configuration**:
```yaml
pipeline:
  iteration:
    enabled: true
    form: 2  # 1 or 2
    max_rounds: 3
    min_quality: "good"
```

### Step 6: Answer Extraction

**Module**: `src/pipeline/step6_extraction.py`

**Purpose**: Extract final high-quality answers.

**Process**:
1. For each image's Q&A pairs:
   - If qlabel == "yes": Include latest answer
   - If qlabel == "no" AND mark == "excellent": Include latest answer
2. Compile all qualifying answers
3. Generate final knowledge base

**Input**:
- `JSONstep5_Iteration_Form2.json` (or Form1)

**Output**:
- `JSONstep6_answerRes.json`: Final extracted answers

**Output Format**:
```json
{
    "pictures": [
        {
            "name": "image1.png",
            "questionRes": ["Q1", "Q2"],
            "answerRes": ["A1", "A2"]
        }
    ],
    "AllanswerRes": ["A1", "A2", ...]
}
```

## Image Categories

The pipeline recognizes 7 image types from CTI reports:

### 1. Attack Flow or Intelligence Structure
- Attack chain diagrams
- Threat actor relationship graphs
- Kill chain visualizations
- Intelligence structure diagrams

**Question Seeds**:
- Main content description
- Possible uses
- Attack techniques involved
- Sequential relationships
- Attack targets

### 2. Malware Code
- Source code snippets
- Scripts and commands
- Decompiled code
- Code analysis results

**Question Seeds**:
- Code functionality
- Possible uses
- Attack techniques
- Variables and functions

### 3. Application Tool Screenshot
- Security tool interfaces
- Command-line outputs
- Configuration panels
- Monitoring dashboards

**Question Seeds**:
- Main content
- Tool purpose
- Key highlighted information
- Attack techniques

### 4. Data Table
- Structured data tables
- Comparison matrices
- Configuration lists
- Indicator tables

**Question Seeds**:
- Table content
- Field descriptions
- Highlighted fields
- Malicious activity indicators

### 5. Charts and Data Visualization
- Statistical charts
- Trend graphs
- Network diagrams
- Timeline visualizations

**Question Seeds**:
- Chart content
- Trends observed
- Conclusions derived
- Data insights

### 6. File Paths and Names
- Directory structures
- File listings
- Path hierarchies
- Registry keys

**Question Seeds**:
- Main content
- File paths included
- System locations
- Attack techniques

### 7. Descriptive Image and Content Explanation
- Textual descriptions
- Annotated images
- Explanatory content
- Documentation screenshots

**Question Seeds**:
- Main content
- Key information
- Explanations provided
- Relevance to threats

## Data Flow

```
Input Data Structure:
└── cti_reports/
    └── 00/
        ├── original/
        │   ├── KG.json
        │   ├── outline.json
        │   └── In-context.json
        └── picture/
            ├── image1.png
            └── image2.png

Processing Flow:
[picture/] + [KG.json] 
    → Step 1 → [JSONstep1_Questions.json]
    → Step 2 → [JSONstep2_Answers.json] (+ In-context.json, outline.json)
    → Step 3 → [JSONstep3_QLabels.json]
    → Step 4 → [JSONstep4_Mark.json]
    → Step 5 → [JSONstep5_Iteration_Form2.json]
    → Step 6 → [JSONstep6_answerRes.json]

Output Data Structure:
└── cti_reports/
    └── 00/
        └── process/
            ├── JSONstep1_Questions.json
            ├── JSONstep2_Answers.json
            ├── JSONstep3_QLabels.json
            ├── JSONstep4_Mark.json
            ├── JSONstep5_Iteration_Form2.json
            └── JSONstep6_answerRes.json
```

## API Requirements

### Alibaba Cloud DashScope (Qwen)
- **Usage**: Steps 1-3, 5 (question generation, answering, judging, iteration)
- **Models**: qwen-max, qwen-vl-max
- **Features**: Multimodal understanding (text + image)

### Evaluation Model (for Step 4)
- **Usage**: Step 4 (answer quality marking)
- **Model**: qwen2.5-72b-instruct (default, configurable)
- **Note**: The interface supports third-party LLMs, but due to service access restrictions, only domestic models are used by default.

## Error Handling

The pipeline includes comprehensive error handling:

1. **API Retry Logic**:
   - Exponential backoff
   - Configurable max retries
   - Timeout management

2. **Response Validation**:
   - Greeting detection and retry
   - Empty response handling
   - Format validation

3. **Thread Safety**:
   - Thread locks for shared resources
   - Exception handling in threads
   - Graceful degradation

4. **Logging**:
   - Detailed error messages
   - Progress tracking
   - Debug information

## Performance Optimization

### Parallel Processing
- Multi-threaded question answering
- Concurrent API calls where possible
- Configurable worker pool size

### Caching
- Reuse CTI context and outline
- Avoid redundant file reads
- Cache API responses (optional)

### Batching
- Process multiple CTI reports in sequence
- Batch similar operations
- Resume from last checkpoint

## Extending the Pipeline

### Adding New Steps

1. Create module in `src/pipeline/`
2. Define input/output format
3. Implement main processing function
4. Add configuration in `config.yaml`
5. Update `run_single_cti.py` and `run_all_cti.py`

### Custom Image Categories

1. Add category to `config.yaml`
2. Define question seeds in Step 1
3. Update classification prompt
4. Test with sample images

### Alternative LLM Providers

1. Create adapter in `src/utils/api_connector.py`
2. Add configuration section
3. Update relevant pipeline steps
4. Test compatibility

## Best Practices

1. **Always backup original data** before processing
2. **Use configuration files** instead of hardcoded values
3. **Monitor API costs** especially with large batches
4. **Review intermediate outputs** to catch issues early
5. **Tune iteration parameters** based on quality requirements
6. **Use version control** for configuration changes

## Troubleshooting

### Common Issues

**Issue**: API timeout errors
- **Solution**: Increase timeout in config, reduce image sizes

**Issue**: Low-quality answers
- **Solution**: Enable iteration, adjust prompts, try different models

**Issue**: Incorrect image classification
- **Solution**: Review classification prompt, add examples

**Issue**: High API costs
- **Solution**: Use smaller models, reduce iteration rounds, cache results

## Future Enhancements

- [ ] Support for additional LLM providers (Claude, Gemini)
- [ ] Streaming API responses
- [ ] Real-time processing mode
- [ ] Distributed processing for large datasets
- [ ] Fine-tuned models for specific CTI domains
- [ ] Active learning for question generation
- [ ] Multi-language support
- [ ] Web-based monitoring dashboard
