import fitz  # PyMuPDF
import json
import os
import re
from collections import Counter
from datetime import datetime
from difflib import SequenceMatcher

# ====================== PDF STRUCTURE EXTRACTOR ====================== #
def extract_body_font_size(doc):
    font_sizes = []
    for page in doc:
        blocks = page.get_text("dict", sort=True).get("blocks", [])
        for block in blocks:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    font_sizes.append(round(span["size"], 1))
    return Counter(font_sizes).most_common(1)[0][0] if font_sizes else 12.0

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text.strip())
    text = re.sub(r'\s*([.,:;!?])\s*', r'\1 ', text)
    return text

def extract_title(page, body_font_size):
    blocks = page.get_text("dict", sort=True).get("blocks", [])
    title_candidates = []

    for block in blocks:
        for line in block.get("lines", []):
            spans = line.get("spans", [])
            text_parts = [span["text"].strip() for span in spans if span["text"].strip()]
            font_sizes = [span["size"] for span in spans if span["text"].strip()]
            if not text_parts:
                continue
            combined_text = clean_text(" ".join(text_parts))
            if len(combined_text) < 5 or combined_text.lower() in ['page', 'of', 'copyright', '©']:
                continue
            bbox = line["bbox"]
            max_size = max(font_sizes)
            page_width = page.rect.width
            is_centered = abs((bbox[0] + bbox[2]) / 2 - page_width / 2) < page_width * 0.15
            if max_size >= body_font_size * 1.2:
                score = max_size + (2 if is_centered else 0) + (1 if bbox[1] < page.rect.height * 0.3 else 0)
                title_candidates.append({"text": combined_text, "score": score, "y_pos": bbox[1]})

    if title_candidates:
        title_candidates.sort(key=lambda x: (-x["score"], x["y_pos"]))
        best_score = title_candidates[0]["score"]
        return " ".join(c["text"] for c in title_candidates if c["score"] >= best_score - 1)
    return ""

def extract_headings(doc, body_font_size):
    headings = []
    seen_texts = set()

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict", sort=True).get("blocks", [])
        for block in blocks:
            for line in block.get("lines", []):
                spans = line.get("spans", [])
                text_parts = [span["text"].strip() for span in spans if span["text"].strip()]
                font_sizes = [span["size"] for span in spans if span["text"].strip()]
                if not text_parts:
                    continue
                combined_text = clean_text(" ".join(text_parts))
                if (len(combined_text) < 3 or combined_text.lower() in seen_texts or 
                    combined_text.isdigit() or combined_text.lower() in ['page', 'of', 'the', 'and', 'or']):
                    continue
                seen_texts.add(combined_text.lower())
                max_size = max(font_sizes)
                if max_size < body_font_size * 1.15:
                    continue
                headings.append({
                    "text": combined_text,
                    "size": round(sum(font_sizes) / len(font_sizes), 1),
                    "page": page_num,
                    "bbox": line["bbox"]
                })
    return headings

def cluster_headings(headings):
    if not headings:
        return []
    unique_sizes = sorted({h["size"] for h in headings}, reverse=True)
    size_to_level = {size: f"H{min(i+1, 4)}" for i, size in enumerate(unique_sizes)}
    for h in headings:
        h["level"] = size_to_level[h["size"]]
    return headings

def extract_paragraphs(page):
    text = page.get_text("text", sort=True)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    paragraphs = []
    current_para = []
    for line in lines:
        if not current_para:
            current_para.append(line)
        else:
            last_line = current_para[-1]
            if (len(last_line) > 50 and len(line) > 50 and 
                not last_line.endswith(('.', '!', '?', ':"', '."')) and
                not line[0].islower()):
                paragraphs.append(" ".join(current_para))
                current_para = [line]
            else:
                current_para.append(line)
    if current_para:
        paragraphs.append(" ".join(current_para))
    return paragraphs

def process_pdf(input_path):
    doc = fitz.open(input_path)
    result = {"title": "", "outline": [], "pages": []}
    body_font_size = extract_body_font_size(doc)

    if doc.page_count > 0:
        result["title"] = extract_title(doc[0], body_font_size)

    headings = extract_headings(doc, body_font_size)
    clustered = cluster_headings(headings)
    clustered.sort(key=lambda x: (x["page"], x["bbox"][1]))

    for h in clustered:
        result["outline"].append({
            "level": h["level"],
            "text": h["text"],
            "page": h["page"] + 1
        })

    for page_num in range(doc.page_count):
        paragraphs = extract_paragraphs(doc[page_num])
        result["pages"].append({
            "page_num": page_num + 1,
            "paragraphs": paragraphs
        })

    doc.close()
    return result

# ====================== IMPROVED DOCUMENT ANALYZER ====================== #
def analyze_documents(json_dir, persona, job):
    documents, filenames = [], []
    for filename in os.listdir(json_dir):
        if filename.endswith(".json"):
            with open(os.path.join(json_dir, filename), "r", encoding="utf-8") as f:
                documents.append(json.load(f))
                filenames.append(filename)

    # Enhanced keyword extraction and scoring
    def get_keywords(text):
        return set(re.findall(r'\b\w{3,}\b', text.lower()))
    
    persona_keywords = get_keywords(persona)
    job_keywords = get_keywords(job)
    all_keywords = persona_keywords.union(job_keywords)
    
    # Special handling for travel planning persona
    travel_keywords = {
        "cities": ["city", "town", "itinerary", "guide", "marseille", "nice", "cannes"],
        "activities": ["things to do", "activities", "adventure", "beach", "hiking", "coastal", "water sports"],
        "food": ["cuisine", "food", "restaurant", "wine", "dining", "culinary"],
        "nightlife": ["nightlife", "bars", "clubs", "entertainment", "party"],
        "logistics": ["hotel", "transport", "tips", "packing", "planning", "advice"]
    }
    
    college_group_keywords = ["group", "friends", "college", "young", "budget", "shared"]
    
    candidate_sections = []
    for doc_idx, doc in enumerate(documents):
        filename = filenames[doc_idx]
        
        for heading in doc.get("outline", []):
            section_text = heading["text"].lower()
            page_num = heading["page"]
            score = 0
            
            # Basic keyword matching
            section_words = get_keywords(section_text)
            score += len(section_words.intersection(all_keywords))
            
            # Domain-specific scoring for travel
            for category, keywords in travel_keywords.items():
                if any(keyword in section_text for keyword in keywords):
                    score += 2
            
            # Boost for college group relevance
            if any(keyword in section_text for keyword in college_group_keywords):
                score += 3
            
            # Get context paragraphs
            context = ""
            for page in doc.get("pages", []):
                if page["page_num"] == page_num:
                    paragraphs = page["paragraphs"]
                    try:
                        # Find heading position in paragraphs
                        idx = next(i for i, p in enumerate(paragraphs) 
                                 if heading["text"].lower() in p.lower())
                        start_idx = min(idx + 1, len(paragraphs) - 1)
                        end_idx = min(start_idx + 3, len(paragraphs))
                        context = "\n\n".join(paragraphs[start_idx:end_idx])
                    except (StopIteration, ValueError):
                        context = "\n\n".join(paragraphs[:2])
                    break
            
            candidate_sections.append({
                "document": filename.replace("_new.json", ".pdf"),
                "page_number": page_num,
                "section_title": heading["text"],
                "score": score,
                "context": context,
                "doc_idx": doc_idx
            })
    
    # Sort by score and select top 5
    candidate_sections.sort(key=lambda x: -x["score"])
    selected_sections = candidate_sections[:5]
    
    # Prepare final output
    extracted_sections = []
    subsection_analysis = []
    
    for rank, section in enumerate(selected_sections, 1):
        extracted_sections.append({
            "document": section["document"],
            "page_number": section["page_number"],
            "section_title": section["section_title"],
            "importance_rank": rank
        })
        
        subsection_analysis.append({
            "document": section["document"],
            "page_number": section["page_number"],
            "refined_text": section["context"]
        })
    
    return {
        "metadata": {
            "input_documents": [f.replace("_new.json", ".pdf") for f in filenames],
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }

# ====================== MAIN EXECUTION ====================== #
if __name__ == "__main__":
    PDF_DIR = r"C:\Users\dell\OneDrive\Desktop\1B\input"
    JSON_DIR = r"C:\Users\dell\OneDrive\Desktop\1B\output"
    OUTPUT_DIR = r"C:\Users\dell\OneDrive\Desktop\1B\results"
    PERSONA = "Travel Planner"
    JOB = "Plan a trip of 4 days for a group of 10 college friends"
    
    # Create directories if needed
    os.makedirs(JSON_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Step 1: Process PDFs to JSON
    for filename in os.listdir(PDF_DIR):
        if filename.lower().endswith(".pdf"):
            input_path = os.path.join(PDF_DIR, filename)
            output_path = os.path.join(JSON_DIR, f"{os.path.splitext(filename)[0]}_new.json")
            
            try:
                print(f"Processing {filename}...")
                result = process_pdf(input_path)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"✔ Created {os.path.basename(output_path)}")
            except Exception as e:
                print(f"❌ Error processing {filename}: {str(e)}")
    
    # Step 2: Analyze documents
    print("\nAnalyzing documents...")
    analysis_result = analyze_documents(JSON_DIR, PERSONA, JOB)
    final_output_path = os.path.join(OUTPUT_DIR, "challenge1b_output.json")
    
    with open(final_output_path, "w", encoding="utf-8") as f:
        json.dump(analysis_result, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Analysis complete. Results saved to:\n{final_output_path}")