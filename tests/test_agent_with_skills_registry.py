import pytest
import os
import shutil
from agent_with_skills_register_user.agent_skill_registry import SkillRegistry

@pytest.fixture
def temp_skills_dir(tmp_path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    
    skill_content = """---
name: test_skill
description: A test skill
---
# Test Skill Content
"""
    skill_file = skills_dir / "test_skill.md"
    skill_file.write_text(skill_content)
    
    return str(skills_dir)

def test_skill_registry_loading(temp_skills_dir):
    registry = SkillRegistry(temp_skills_dir)
    assert "test_skill" in registry.skills
    assert registry.skills["test_skill"].metadata.name == "test_skill"
    assert "Test Skill Content" in registry.skills["test_skill"].content

def test_skill_registry_search(temp_skills_dir):
    registry = SkillRegistry(temp_skills_dir)
    results = registry.search_skills("test")
    assert len(results) == 1
    assert results[0].name == "test_skill"

    results = registry.search_skills("nonexistent")
    assert len(results) == 0

def test_skill_registry_get(temp_skills_dir):
    registry = SkillRegistry(temp_skills_dir)
    skill = registry.get_skill("test_skill")
    assert skill is not None
    assert skill.metadata.name == "test_skill"

    skill = registry.get_skill("invalid")
    assert skill is None
