from app.translation.glossary import get_glossary_for_language, GLOSSARY

def test_glossary_hindi():
    glossary = get_glossary_for_language("hindi")
    assert "Intellectual Property" in glossary
    assert glossary["Intellectual Property"] == "बौद्धिक संपदा"
    assert "Patent" in glossary
    assert glossary["Patent"] == "पेटेंट"

def test_glossary_tamil():
    glossary = get_glossary_for_language("tamil")
    assert "Copyright" in glossary
    assert glossary["Copyright"] == "பதிப்புரிமை"

def test_glossary_case_insensitive():
    glossary = get_glossary_for_language("Hindi")
    assert "Patent" in glossary

def test_glossary_all_languages():
    for lang in ["hindi", "marathi", "bengali", "gujarati", "tamil", "telugu"]:
        glossary = get_glossary_for_language(lang)
        assert len(glossary) > 0, f"No glossary entries for {lang}"

def test_glossary_unknown_language():
    glossary = get_glossary_for_language("french")
    assert len(glossary) == 0
