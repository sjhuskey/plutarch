#!/usr/bin/env python3
"""
Section Extraction Script for NLP Corpus Preparation

This script processes all plain text files in a specified input directory, splits each file into sections based on recognizable section headers (e.g., "LIFE OF ..." or "COMPARISON OF ..."), removes non-semantic line breaks (i.e., joins lines within paragraphs), and writes each section to a separate output file. Output files are named for both the source file and the section title to ensure uniqueness and traceability

Intended for use in preparing corpora for Natural Language Processing tasks.

Usage:
    python preprocess_texts.py <input_directory> <output_directory>

author: Samuel J. Huskey
date: 2025-09-01
"""

import re
from pathlib import Path

def preserve_poetry_linebreaks(text):
    """
    Preserve line breaks in poetry while removing non-semantic breaks.
    args: 
        text (str): The input text to process.
    returns: 
        str: The processed text with preserved poetry line breaks.
    """
    # Step 1: Replace poetry line breaks (lines starting with 4 spaces) with a marker
    text = re.sub(r"(\n)( {4})", r"<POETRY_LB>\2", text)
    # Step 2: Remove non-semantic line breaks elsewhere
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    # Step 3: Restore poetry line breaks
    text = text.replace("<POETRY_LB>", "\n")
    return text

# Remove footnote indicators from text documents
def remove_unwanted_text(text):
    """
    Removes unwanted text patterns (e.g., footnote indicators, Plutarch's Lives references) from the text.
    args:
        text (str): The input text to process.
    returns:
        str: The processed text with unwanted text removed.
    """
    text = re.sub(r"\[\d+\]", "", text)
    text = re.sub(r"PLUTARCH'S LIVES.? \([^)]+\)", "", text)
    return text

# Remove FOOTNOTES section from text documents
def remove_footnotes(text):
    """
    Removes the 'FOOTNOTES:' section and everything after it.
    args:
        text (str): The input text to process.
    returns:
        str: The processed text with footnotes removed.
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip().lower().startswith("footnotes:"):
            return "\n".join(lines[:i]).rstrip()  # Drop everything from here to the end
        if line.strip().lower().startswith("[footnote "):
            return "\n".join(lines[:i]).rstrip()  # Drop everything from here to the end
    return text  # Return unchanged if no 'FOOTNOTES:' found 

def process_file(input_directory, output_directory):
    """
    Process all text files in the input directory and save the cleaned versions to the output directory.
    args:
        input_directory (Path): The directory containing the input text files.
        output_directory (Path): The directory to save the cleaned text files.
    Returns:
        None
    """
    for file_path in input_directory.glob("*.txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            original_text = f.read()
            # Replace Æ and æ with AE and ae
            original_text = original_text.replace("Æ", "AE").replace("æ", "ae")
            # Replace Œ and œ with OE and oe
            original_text = original_text.replace("Œ", "OE").replace("œ", "oe")
            # Regular expression pattern to match section headers
            # Matches lines starting with "LIFE OF ..." or "COMPARISON OF ..."
            section_pattern = re.compile(r"^(LIFE OF [A-Z .]+|COMPARISON OF[^\n]*)$", re.MULTILINE)
            matches = list(section_pattern.finditer(original_text))
            for i, match in enumerate(matches):
                start = match.start()  # Start index of the section
                end = matches[i + 1].start() if i + 1 < len(matches) else len(original_text)  # End index

                # Clean and format the section title for use in the filename
                section_title = match.group(1).strip().replace(" ", "_").replace(".", "")
                # Extract the section text
                section_text = original_text[start:end].strip()

                # Remove non-semantic line breaks within the section
                reformatted_poetry = preserve_poetry_linebreaks(section_text)
                print(f"Preserved poetry line breaks in: {file_path.name}")
                no_footnotes = remove_footnotes(reformatted_poetry)
                print(f"Removed footnotes from: {file_path.name}")
                cleaned_text = remove_unwanted_text(no_footnotes)
                print(f"Removed unwanted text from: {file_path.name}")

                out_file = (
                    output_directory / f"{file_path.stem}_{i+1:02d}_{section_title}.txt"
                )
                with open(out_file, "w", encoding="utf-8") as f:
                    f.write(cleaned_text)
                    print(f"Processed: {file_path.name} → {out_file.name}")

input_directory = Path("../data/text")
output_directory = Path("../cleaned_text")
output_directory.mkdir(parents=True, exist_ok=True)
process_file(input_directory, output_directory)