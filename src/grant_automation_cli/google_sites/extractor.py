"""
Google Sites Data Extractor

DEVELOPER GUIDELINE: Robust Data Extraction
Parses markdown templates into structured dictionaries. Use defensive 
parsing strategies and handle missing or malformed data gracefully without 
crashing the extraction process.
"""

import os
import re


def extract_business_profile(filepath: str) -> dict:
    """Parses business_profile.md into a dictionary."""
    data = {}
    if not os.path.exists(filepath):
        return data
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Basic info
    data['name'] = _extract_bracket_value(content, r'\*\*Business Name:\*\*\s*\[(.*?)\]')
    data['tagline'] = _extract_bracket_value(content, r'\*\*Tagline:\*\*\s*\[(.*?)\]')
    data['description'] = _extract_bracket_value(content, r'\*\*Description:\*\*\s*\[(.*?)\]')
    
    # Assets
    data['logo_url'] = _extract_bracket_value(content, r'\*\*Logo URL:\*\*\s*\[(.*?)\]')
    data['favicon_url'] = _extract_bracket_value(content, r'\*\*Favicon URL:\*\*\s*\[(.*?)\]')
    
    return data

def extract_design_preferences(filepath: str) -> dict:
    """Parses design_preferences.md into a dictionary."""
    data = {}
    if not os.path.exists(filepath):
        return data
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Theme selection - looking for [x] or [X]
    theme_match = re.search(r'-\s+\[[xX]\]\s+([A-Za-z]+)', content)
    data['theme'] = theme_match.group(1).lower() if theme_match else 'simple'
    
    # Primary color
    data['primary_color'] = _extract_bracket_value(content, r'\*\*Primary Brand Color \(Hex Code\):\*\*\s*\[(.*?)\]')
    
    # Navigation layout
    nav_match = re.search(r'Choose where the navigation menu should appear:\s*(?:-\s+\[ \]\s+[A-Za-z]+\s*)*-\s+\[[xX]\]\s+([A-Za-z]+)', content)
    data['nav_layout'] = nav_match.group(1).lower() if nav_match else 'top'
    
    return data

def extract_page_content(filepath: str) -> list:
    """Parses page_content.md into a list of dictionaries representing pages."""
    pages = []
    if not os.path.exists(filepath):
        return pages
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    page_sections = content.split('## Page:')[1:] # Skip the intro part
    
    for section in page_sections:
        lines = section.strip().split('\n')
        page_name = lines[0].strip()
        
        page_data = {
            'name': page_name,
            'title': _extract_bracket_value(section, r'\*\*Title:\*\*\s*(.*)'),
            'header_type': _extract_bracket_value(section, r'\*\*Header Type:\*\*\s*\[(.*?)\]'),
            'blocks': [] # Simplified: we'd parse blocks here in a full implementation
        }
        pages.append(page_data)
        
    return pages

def _extract_bracket_value(content: str, pattern: str) -> str:
    match = re.search(pattern, content)
    if match:
        val = match.group(1).strip()
        # Handle cases where user leaves default instructions like [Enter your...]
        if val.startswith('Enter') or val.startswith('URL'):
            return ''
        return val
    return ''
