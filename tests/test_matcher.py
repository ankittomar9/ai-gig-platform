import pytest
from pathlib import Path
from app.services.matcher import (
    extract_skills_from_text,
    calculate_match_score,
    extract_text_from_file
)

def test_extract_skills_acronym_casing():
    text = "We need strong skills in SQL, API design, RLHF, LLM evaluation, AWS, GCP, Python, and Docker."
    skills = extract_skills_from_text(text)
    assert "SQL" in skills
    assert "API" in skills
    assert "RLHF" in skills
    assert "LLM" in skills
    assert "AWS" in skills
    assert "GCP" in skills
    assert "Python" in skills
    assert "Docker" in skills
    # Ensure no lowercase/title mistakes
    assert "Sql" not in skills
    assert "Api" not in skills
    assert "Rlhf" not in skills

def test_calculate_match_score_title_bonus_capped():
    # Long title with many words
    title = "Python Java Docker Linux SQL API Machine Learning React Git Kubernetes Cloud Backend Engineer"
    desc = "Looking for an engineer"
    user_skills = ["Python", "SQL", "Docker", "Java", "Linux"]
    resume = "Experienced with Python, Java, Docker, Linux, SQL, API."

    score, matched = calculate_match_score(title, desc, user_skills, resume)
    # Total score cannot exceed 98 and title bonus is capped at 20
    assert 20 <= score <= 98
    assert len(matched) >= 3

def test_extract_text_corrupted_docx(tmp_path):
    corrupt_file = tmp_path / "corrupt.docx"
    corrupt_file.write_bytes(b"PK\x03\x04invalid-zip-docx-header")
    with pytest.raises(ValueError, match="Failed to extract text from .docx file"):
        extract_text_from_file(corrupt_file)

def test_extract_text_empty_txt(tmp_path):
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("   \n\t  ", encoding="utf-8")
    with pytest.raises(ValueError, match="The uploaded text document is empty"):
        extract_text_from_file(empty_file)

def test_extract_text_unsupported_extension(tmp_path):
    unsupported = tmp_path / "resume.pdf"
    unsupported.write_bytes(b"%PDF-1.4")
    with pytest.raises(ValueError, match="Unsupported file format"):
        extract_text_from_file(unsupported)
