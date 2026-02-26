# Changelog

All notable changes to MM-AttacKG will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive README with project overview and architecture
- Configuration management with YAML and environment variables
- Logging utilities with colored console output
- MIT License
- Contributing guidelines
- .gitignore for Python projects
- Setup.py for package installation
- Documentation (pipeline, examples, full demo, API interfaces)

### Changed
- Reorganized code into `src/pipeline/` and `src/utils/`
- Renamed files to follow Python naming conventions

## [0.1.0] - 2025-02-03

### Initial Release
- 6-step processing pipeline for CTI image analysis
- Question generation based on image classification
- Answer generation using multimodal LLMs
- Theme-based filtering for cybersecurity relevance
- Answer quality marking and evaluation
- Iterative answer refinement (Form 1 and Form 2)
- Final answer extraction
- Support for 7 image categories
- MITRE ATT&CK framework integration
- STIX 2.1 entity type support
- Batch processing for multiple CTI reports
