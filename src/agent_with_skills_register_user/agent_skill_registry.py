import os
import re
from typing import Dict, List, Optional
from pydantic import BaseModel
from rank_bm25 import BM25Okapi

class SkillMetadata(BaseModel):
    name: str
    description: str
    tools: List[str] = []

class Skill(BaseModel):
    metadata: SkillMetadata
    content: str
    path: str

class SkillRegistry:
    def __init__(self, skills_dir: str):
        self.skills_dir = skills_dir
        self.skills: Dict[str, Skill] = {}
        self.bm25: Optional[BM25Okapi] = None
        self.skill_names: List[str] = []
        self.refresh()

    def refresh(self):
        self.skills = {}
        self.skill_names = []
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
                        self.skill_names.append(skill.metadata.name)
        
        # Initialize BM25
        if self.skills:
            corpus = []
            for name in self.skill_names:
                skill = self.skills[name]
                # Combine name and description for indexing
                text = f"{skill.metadata.name} {skill.metadata.description} {skill.content}"
                corpus.append(self._tokenize(text))
            self.bm25 = BM25Okapi(corpus)

    def _tokenize(self, text: str) -> List[str]:
        # BM25 works better with slightly more aggressive tokenization and filtering
        tokens = re.findall(r"\w+", text.lower())
        # Filter out short tokens if necessary, but keep it simple for PoC
        return tokens

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

        # Parse tools if present, handle comma-separated list
        tools_list = []
        if "tools" in metadata:
            tools_list = [t.strip() for t in metadata["tools"].split(",") if t.strip()]

        return Skill(
            metadata=SkillMetadata(
                name=metadata["name"], 
                description=metadata["description"],
                tools=tools_list
            ),
            content=body,
            path=filepath
        )

    def search_skills(self, query: str, top_k: int = 3) -> List[SkillMetadata]:
        if not self.skills:
            return []
            
        # Fallback to simple substring match if BM25 is not initialized or query is short
        query_lower = query.lower()
        substring_results = []
        for skill in self.skills.values():
            if (query_lower in skill.metadata.name.lower() or 
                query_lower in skill.metadata.description.lower()):
                substring_results.append(skill.metadata)
        
        if not self.bm25:
            return substring_results[:top_k]

        tokenized_query = self._tokenize(query)
        if not tokenized_query:
            return substring_results[:top_k]

        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top K indices
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        
        bm25_results = []
        for i in top_indices:
            if scores[i] > 0:
                name = self.skill_names[i]
                bm25_results.append(self.skills[name].metadata)
        
        # Combine and deduplicate (preserving BM25 order for hits)
        seen_names = set()
        final_results = []
        
        for res in bm25_results + substring_results:
            if res.name not in seen_names:
                final_results.append(res)
                seen_names.add(res.name)
                
        return final_results[:top_k]

    def get_skill(self, name: str) -> Optional[Skill]:
        return self.skills.get(name)

    def list_all_skills(self) -> List[SkillMetadata]:
        return [skill.metadata for skill in self.skills.values()]
