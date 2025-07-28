# Adobe-Hackathon2
# Persona-Driven Document Intelligence - Round 1B

## Overview
This solution implements an intelligent document analyst that extracts and prioritizes relevant sections from PDF documents based on a specific persona and their job-to-be-done.

## Requirements
- Docker
- PDF documents to analyze

## Quick Start

### 1. Build the Docker Image
bash
docker build -t persona-doc-intelligence .


### 2. Prepare Input
Place your PDF documents in a directory (e.g., ./input/)

### 3. Run the Analysis
bash
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output persona-doc-intelligence


### 4. View Results
The output will be saved as challenge1b_output.json in the ./output/ directory.

## Configuration

### Environment Variables
You can customize the persona and job by modifying the environment variables in the Dockerfile or by passing them at runtime

### Input Format
- Place PDF documents in the input directory
- The system will process all PDF files found in the directory
- Supports 3-10 documents as specified in the requirements

### Output Format
The system generates a JSON file with the following structure:
- *metadata*: Input documents, persona, job, and timestamp
- *extracted_sections*: Ranked list of relevant sections with page numbers
- *sub_section_analysis*: Refined text extracts from important sections

## Performance Characteristics
- *CPU-only operation*: No GPU required
- *Model size*: < 1GB memory usage
- *Processing time*: < 60 seconds for 3-5 documents
- *No internet access*: Fully offline operation

## Supported Use Cases
- Academic research papers
- Business reports and financial documents
- Educational content and textbooks
- Any domain-specific PDF documents

## Troubleshooting
- Ensure PDF files are not corrupted or password-protected
- Check that input directory contains at least one PDF file
- Verify sufficient disk space for output generation
