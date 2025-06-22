import pandas as pd
import json
from pathlib import Path
import os

def process_bible_version(version_file):
    """Process a single Bible version CSV file"""
    df = pd.read_csv(version_file)
    
    # Group by book and chapter
    grouped = df.groupby(['b', 'c'])
    
    # Process each group
    bible_data = []
    for (book, chapter), group in grouped:
        verses = []
        for _, row in group.iterrows():
            verse_number = int(row['v'])  # Convert to int
            verse_text = row['t']
            verses.append(f"{verse_text} ({verse_number})")
        
        bible_data.append({
            'book': int(book),  # Convert to int
            'chapter': int(chapter),  # Convert to int
            'verses': verses
        })
    
    return bible_data

def process_all_versions():
    """Process all Bible versions and create a combined dataset"""
    dataset_path = Path('bible_dataset')
    versions = [
        't_kjv.csv',  # King James Version
        't_web.csv',  # World English Bible
        't_ylt.csv'   # Young's Literal Translation
    ]
    
    all_data = []
    
    # Process each version
    for version in versions:
        version_path = dataset_path / version
        if version_path.exists():
            print(f"Processing {version}...")
            data = process_bible_version(version_path)
            all_data.extend(data)
    
    # Save processed data
    with open('processed_bible_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print("Processing complete!")

if __name__ == "__main__":
    process_all_versions()
