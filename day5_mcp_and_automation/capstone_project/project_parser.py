import re
from pathlib import Path
from typing import List, Dict, Any

class ProjectParser:
    """Parses capstone projects from the README.md file dynamically."""

    def __init__(self, readme_path: Path):
        self.readme_path = readme_path

    def parse(self) -> List[Dict[str, Any]]:
        """Parses the README file and returns a list of project dictionaries."""
        if not self.readme_path.exists():
            raise FileNotFoundError(f"README.md file not found at {self.readme_path}")

        content = self.readme_path.read_text(encoding="utf-8")
        
        # Split content by markdown horizontal rules or project headings to isolate projects
        # Let's find all project headings of the form: ## <number>. <title>
        project_sections = re.split(r'\n##\s+(?=\d+\.\s+)', content)
        
        projects = []
        
        # The first section is the header/overview, skip it
        for section in project_sections[1:]:
            # We want to extract:
            # - ID & Title: e.g., "1. ExamCraft – Intelligent Question Paper Generator"
            # - Stream: **Engineering Stream:** ECE
            # - Paradigm: **Primary AI Paradigm:** Agentic AI
            # - Difficulty: **Difficulty Level:** Intermediate
            # - Description: Content between "### Project Description" and the next heading
            # - Key Features: Bullet points under "### Key Features"
            # - Expected Outcome: Text under "### Expected Outcome"
            
            lines = section.strip().split('\n')
            if not lines:
                continue
                
            heading = lines[0].strip()
            heading_match = re.match(r'(\d+)\.\s*(.+)', heading)
            if not heading_match:
                continue
                
            proj_id = int(heading_match.group(1))
            proj_title = heading_match.group(2).strip()
            
            section_text = '\n'.join(lines[1:])
            
            # Extract metadata using regex
            stream_match = re.search(r'\*\*Engineering\s+Stream:\*\*\s*(.+)', section_text, re.IGNORECASE)
            paradigm_match = re.search(r'\*\*Primary\s+AI\s+Paradigm:\*\*\s*(.+)', section_text, re.IGNORECASE)
            difficulty_match = re.search(r'\*\*Difficulty\s+Level:\*\*\s*(.+)', section_text, re.IGNORECASE)
            
            stream = stream_match.group(1).strip() if stream_match else "N/A"
            paradigm = paradigm_match.group(1).strip() if paradigm_match else "N/A"
            difficulty = difficulty_match.group(1).strip() if difficulty_match else "N/A"
            
            # Extract sections: Description, Features, Outcome
            # Description is after "### Project Description" up to next "###" or end of text
            description_match = re.search(
                r'###\s+Project\s+Description\s*\n(.*?)(?=\n###|\Z)', 
                section_text, 
                re.DOTALL | re.IGNORECASE
            )
            description = description_match.group(1).strip() if description_match else ""
            
            # Key features
            features_match = re.search(
                r'###\s+Key\s+Features\s*\n(.*?)(?=\n###|\Z)', 
                section_text, 
                re.DOTALL | re.IGNORECASE
            )
            features = []
            if features_match:
                # Find all bullet points
                bullets = re.findall(r'^\s*[\*\-]\s*(.+)', features_match.group(1), re.MULTILINE)
                features = [b.strip() for b in bullets]
                
            # Expected outcome
            outcome_match = re.search(
                r'###\s+Expected\s+Outcome\s*\n(.*?)(?=\n###|---|\Z)', 
                section_text, 
                re.DOTALL | re.IGNORECASE
            )
            outcome = outcome_match.group(1).strip() if outcome_match else ""
            
            projects.append({
                "id": proj_id,
                "title": proj_title,
                "stream": stream,
                "paradigm": paradigm,
                "difficulty": difficulty,
                "description": description,
                "features": features,
                "outcome": outcome
            })
            
        return projects

# If run directly, print parsed projects to verify
if __name__ == "__main__":
    readme = Path(__file__).parent / "README.md"
    parser = ProjectParser(readme)
    try:
        projs = parser.parse()
        print(f"Successfully parsed {len(projs)} projects:")
        for p in projs:
            print(f"- [{p['id']}] {p['title']} ({p['stream']}) - Paradigm: {p['paradigm']}")
    except Exception as e:
        print(f"Error parsing projects: {e}")
