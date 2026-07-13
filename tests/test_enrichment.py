from app.services.enrichment import get_technique_detail

def test_know_technique():
    result = get_technique_detail("T1059")

    assert result is not None
    assert result["technique_id"] == "T1059"
    assert result["name"]
    assert isinstance(result["tactics"], list)
    assert isinstance(result["data_sources"], list)

def test_unknow_technique_returns_none():
    result = get_technique_detail("T99999")
    
    assert result is None

def test_subtechnique_lookup():
    result = get_technique_detail("T1059")

    assert result is not None
    assert isinstance(result["sub_techniques"], list)

    assert all(
        tech.startswith("T1059.")
        for tech in result["sub_techniques"]
    )