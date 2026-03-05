import os
import pytest

from grant_automation_cli.google_sites import extractor

def test_extract_business_profile(tmp_path):
    business_file = tmp_path / "business_profile.md"
    business_file.write_text("**Business Name:** [Test Business]\n**Tagline:** [Test Tagline]\n**Description:** [Test Description]\n**Logo URL:** [https://test.com/logo.png]\n**Favicon URL:** [https://test.com/favicon.png]\n")
    
    data = extractor.extract_business_profile(str(business_file))
    
    assert data['name'] == "Test Business"
    assert data['tagline'] == "Test Tagline"
    assert data['description'] == "Test Description"
    assert data['logo_url'] == "https://test.com/logo.png"

def test_extract_design_preferences(tmp_path):
    design_file = tmp_path / "design_preferences.md"
    design_file.write_text("- [X] Aristotle\n**Primary Brand Color (Hex Code):** [#FF0000]\nChoose where the navigation menu should appear:\n- [ ] Top\n- [X] Side")
    
    data = extractor.extract_design_preferences(str(design_file))
    
    assert data['theme'] == "aristotle"
    assert data['primary_color'] == "#FF0000"
    assert data['nav_layout'] == "side"

def test_extract_page_content(tmp_path):
    page_file = tmp_path / "page_content.md"
    page_file.write_text("intro text\n## Page: Home\n**Title:** Welcome\n**Header Type:** [Banner]\n\n## Page: About\n**Title:** About Us\n**Header Type:** [Title Only]")
    
    pages = extractor.extract_page_content(str(page_file))
    
    assert len(pages) == 2
    assert pages[0]['name'] == 'Home'
    assert pages[0]['title'] == 'Welcome'
    assert pages[0]['header_type'] == 'Banner'
    assert pages[1]['name'] == 'About'
    assert pages[1]['title'] == 'About Us'
    assert pages[1]['header_type'] == 'Title Only'
