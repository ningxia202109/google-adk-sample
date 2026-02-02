import os
import re
from typing import Dict, List, Optional
from pydantic import BaseModel

class SkillMetadata(BaseModel):
    name: str
    description: str

class Skill(BaseModel):
    metadata: SkillMetadata
    content: str
    path: str

class SkillRegistry:
    def __init__(self, skills_dir: str):
        self.skills_dir = skills_dir
        self.skills: Dict[str, Skill] = {}
        self.refresh()

    def refresh(self):
        self.skills = {}
        if not os.path.exists(self.skills_dir):
            return

        for filename in os.listdir(self.skills_dir):
            if filename.endswith(".md"):
                filepath = os.path.join(self.skills_dir, filename)
                with open(filepath, "r") as f:
                    content = f.read()
                    skill = self._parse_skill(content, filepath)
                    if skill:
                        self.skills[skill.metadata.name] = skill

    def _parse_skill(self, content: str, filepath: str) -> Optional[Skill]:
        # Simple frontmatter parser
        match = re.search(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
        if not match:
            return None

        frontmatter_str = match.group(1)
        body = match.group(2)

        metadata = {}
        for line in frontmatter_str.split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                metadata[key.strip()] = val.strip()

        if "name" not in metadata or "description" not in metadata:
            return None

        return Skill(
            metadata=SkillMetadata(name=metadata["name"], description=metadata["description"]),
            content=body,
            path=filepath
        )

    def search_skills(self, query: str) -> List[SkillMetadata]:
        results = []
        query_lower = query.lower()
        for skill in self.skills.values():
            if query_lower in skill.metadata.name.lower() or query_lower in skill.metadata.description.lower():
                results.append(skill.metadata)
        return results

    def get_skill(self, name: str) -> Optional[Skill]:
        return self.skills.get(name)

    def list_all_skills(self) -> List[SkillMetadata]:
        return [skill.metadata for skill in self.skills.values()]
