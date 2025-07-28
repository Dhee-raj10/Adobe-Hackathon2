# Persona-Driven Document Intelligence - Round 1B

## 🎯 Challenge Overview

This solution implements an intelligent document analyst that extracts and prioritizes the most relevant sections from a collection of PDF documents based on a specific persona and their job-to-be-done.

**Theme**: "Connect What Matters — For the User Who Matters"

## 🚀 Features

- **Persona-Driven Analysis**: Extracts relevant content based on specific user roles and tasks
- **Multi-Domain Support**: Works with research papers, financial reports, textbooks, and more
- **Hybrid Ranking**: Combines semantic similarity with document structure analysis
- **Fast Processing**: Optimized for processing 3-5 documents within 60 seconds
- **CPU-Only**: No GPU required, runs efficiently on standard hardware
- **Offline Operation**: No internet access needed during execution

## 📋 Requirements

- Docker
- PDF documents to analyze (3-10 documents)
- Minimum 1GB RAM available

## 🛠️ Quick Start

### Option 1: Using Docker (Recommended)

1. **Build the Docker image**:
   ```bash
   docker build -t persona-doc-intelligence .
   ```

2. **Prepare your documents**:
   - Place PDF files in a directory (e.g., `./input/`)
   - Ensure documents are not password-protected

3. **Run the analysis**:
   ```bash
   docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output persona-doc-intelligence
   ```

4. **View results**:
   - Check `./output/challenge1b_output.json` for the analysis results

### Option 2: Local Python Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the analysis**:
   ```bash
   python deepseek_python_20250728_b0f689.py
   ```

## ⚙️ Configuration

### Environment Variables

You can customize the analysis by setting environment variables:

```bash
# Set persona and job
export PERSONA="PhD Researcher in Computational Biology"
export JOB="Prepare a comprehensive literature review focusing on methodologies"

# Set input/output directories
export INPUT_DIR="./input"
export OUTPUT_DIR="./output"

# Run the analysis
python deepseek_python_20250728_b0f689.py
```

### Example Personas and Jobs

| Persona | Job-to-be-Done |
|---------|----------------|
| PhD Researcher in Computational Biology | Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks |
| Investment Analyst | Analyze revenue trends, R&D investments, and market positioning strategies |
| Undergraduate Chemistry Student | Identify key concepts and mechanisms for exam preparation on reaction kinetics |
| Journalist | Extract key insights and quotes for a news article on technological developments |
| Entrepreneur | Analyze market opportunities and competitive landscape from business reports |

## 📊 Output Format

The system generates a JSON file with the following structure:

```json
{
  "metadata": {
    "input_documents": ["document1.pdf", "document2.pdf"],
    "persona": "PhD Researcher in Computational Biology",
    "job_to_be_done": "Prepare a comprehensive literature review...",
    "processing_timestamp": "2024-01-15T10:30:00.000000"
  },
  "extracted_sections": [
    {
      "document": "research_paper_1.pdf",
      "page_number": 3,
      "section_title": "Methodology: Graph Neural Network Architecture",
      "importance_rank": 1
    }
  ],
  "sub_section_analysis": [
    {
      "document": "research_paper_1.pdf",
      "refined_text": "We propose a novel Graph Neural Network architecture...",
      "page_number_constraints": 3
    }
  ]
}
```

## 🔧 Technical Details

### Architecture

- **Document Processing**: PyMuPDF for PDF text extraction with structural analysis
- **Content Analysis**: TF-IDF vectorization with cosine similarity for semantic matching
- **Ranking Algorithm**: Hybrid scoring combining semantic relevance (70%) and structural importance (30%)
- **Performance**: Optimized for <60 seconds processing time on 3-5 documents

### Supported Document Types

- Academic research papers
- Business reports and financial documents
- Educational content and textbooks
- News articles and reports
- Technical documentation
- Any domain-specific PDF documents

## 📈 Performance Characteristics

- **Processing Speed**: < 60 seconds for 3-5 documents
- **Memory Usage**: < 1GB total
- **CPU Requirements**: Standard CPU, no GPU needed
- **Document Limit**: 3-10 PDF documents per analysis
- **File Size**: Handles documents up to 50MB each

## 🧪 Testing

### Test Cases Included

1. **Academic Research**: Graph Neural Networks for Drug Discovery
2. **Business Analysis**: Financial reports and market analysis
3. **Educational Content**: Chemistry textbook chapters

### Running Tests

```bash
# Test with research persona
export PERSONA="PhD Researcher in Computational Biology"
export JOB="Prepare a comprehensive literature review focusing on methodologies"
python deepseek_python_20250728_b0f689.py

# Test with investment analyst persona
export PERSONA="Investment Analyst"
export JOB="Analyze revenue trends and market positioning"
python deepseek_python_20250728_b0f689.py
```

## 🐛 Troubleshooting

### Common Issues

1. **No PDF files found**:
   - Ensure PDF files are in the input directory
   - Check file extensions are `.pdf` (lowercase)

2. **Processing errors**:
   - Verify PDF files are not corrupted or password-protected
   - Check sufficient disk space for output generation

3. **Docker issues**:
   - Ensure Docker is running
   - Check volume mount permissions

### Error Messages

- `"No PDF documents found in input directory"`: Add PDF files to input folder
- `"Content too short for proper analysis"`: PDF may be empty or corrupted
- `"need font file or buffer"`: PDF creation issue (rare)

## 📝 License

This project is developed for the Persona-Driven Document Intelligence challenge.

## 🤝 Contributing

This is a competition submission. For questions or issues, please refer to the challenge documentation.

---

**Note**: This solution is designed to work offline and does not require internet access during execution. All processing is done locally using CPU resources only. 