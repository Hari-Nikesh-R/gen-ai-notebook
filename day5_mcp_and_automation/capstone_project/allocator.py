import csv
import json
import random
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

class ProjectAllocator:
    """Manages the registration of teams/students and allocates them to projects using robust lot-drawing algorithms."""

    def __init__(self, projects: List[Dict[str, Any]]):
        self.projects = projects
        self.teams: List[str] = []
        self.allocations: Dict[str, Dict[str, Any]] = {} # team_name -> project_details

    def load_teams_from_file(self, file_path: Path) -> int:
        """Loads team/student names from a file (TXT or CSV). Returns the number of loaded teams."""
        if not file_path.exists():
            raise FileNotFoundError(f"Team file not found at {file_path}")
            
        loaded_teams = []
        suffix = file_path.suffix.lower()
        
        if suffix == '.csv':
            with open(file_path, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:
                        # Clean and append the first non-empty column
                        team_name = row[0].strip()
                        if team_name and not team_name.lower().startswith('team') and len(row) > 1:
                            # Might be a header like Name, Team. Let's filter common headers
                            if 'name' in team_name.lower() or 'team' in team_name.lower():
                                continue
                        if team_name:
                            loaded_teams.append(team_name)
        else: # Default text file line-by-line
            with open(file_path, mode='r', encoding='utf-8') as f:
                for line in f:
                    team_name = line.strip()
                    if team_name:
                        loaded_teams.append(team_name)
                        
        self.teams = list(set(loaded_teams)) # De-duplicate
        # Retain order for UI consistency
        self.teams.sort()
        return len(self.teams)

    def set_teams(self, teams_list: List[str]):
        """Directly sets the list of teams/students."""
        self.teams = list(set([t.strip() for t in teams_list if t.strip()]))
        self.teams.sort()

    def allocate(self, mode: str = "balanced", custom_cap: Optional[int] = None) -> Dict[str, Dict[str, Any]]:
        """
        Allocates teams to projects randomly based on the selected mode:
        
        - 'balanced': Automatically ensures perfectly even distribution.
          e.g. if 10 teams and 8 projects, 2 projects get 2 teams, and 6 projects get 1 team.
        - 'custom_limit': Uses a user-specified capacity limit per project.
        
        Returns a dictionary mapping team name to project details.
        """
        if not self.teams:
            raise ValueError("No teams registered. Load or add teams before allocating.")
        if not self.projects:
            raise ValueError("No projects available for allocation.")

        num_teams = len(self.teams)
        num_projects = len(self.projects)
        
        # Prepare team list copy and shuffle to ensure complete randomness
        shuffled_teams = list(self.teams)
        random.shuffle(shuffled_teams)
        
        slots_pool: List[Dict[str, Any]] = []
        
        if mode == "balanced":
            # Determine base allocation per project and remainder
            base_count = num_teams // num_projects
            remainder = num_teams % num_projects
            
            # Shuffle projects to randomly decide which ones get the remainder (extra team slot)
            shuffled_projects = list(self.projects)
            random.shuffle(shuffled_projects)
            
            for i, project in enumerate(shuffled_projects):
                # How many slots for this project?
                capacity = base_count + (1 if i < remainder else 0)
                slots_pool.extend([project] * capacity)
                
        elif mode == "custom_limit":
            cap = custom_cap if custom_cap is not None else 1
            min_required_cap = (num_teams + num_projects - 1) // num_projects
            if cap < min_required_cap:
                raise ValueError(
                    f"Custom capacity limit {cap} is too low for {num_teams} teams and {num_projects} projects. "
                    f"Minimum required capacity is {min_required_cap}."
                )
            
            # Create a pool of (capacity * projects) slots
            for project in self.projects:
                slots_pool.extend([project] * cap)
                
            # Shuffle the entire pool and slice it to match the number of teams
            random.shuffle(slots_pool)
            slots_pool = slots_pool[:num_teams]
            
        else:
            raise ValueError(f"Unknown allocation mode: {mode}")
            
        # Shuffle the final slot pool one more time to maximize random spread
        random.shuffle(slots_pool)
        
        # Zip shuffled teams with project slots
        self.allocations = {}
        for team, project in zip(shuffled_teams, slots_pool):
            self.allocations[team] = project
            
        return self.allocations

    def get_project_stats(self) -> Dict[int, List[str]]:
        """Returns statistics on allocations, grouped by project ID."""
        stats = {p["id"]: [] for p in self.projects}
        for team, project in self.allocations.items():
            stats[project["id"]].append(team)
        return stats

    def export_csv(self, file_path: Path):
        """Exports the current allocations to a CSV file."""
        if not self.allocations:
            raise ValueError("No allocations to export. Run allocation first.")
            
        with open(file_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Team/Student", "Project ID", "Project Title", "Engineering Stream", "Primary AI Paradigm", "Difficulty Level"])
            for team, proj in sorted(self.allocations.items()):
                writer.writerow([
                    team, 
                    proj["id"], 
                    proj["title"], 
                    proj["stream"], 
                    proj["paradigm"], 
                    proj["difficulty"]
                ])

    def export_json(self, file_path: Path):
        """Exports the allocations and project statistics to a JSON file."""
        if not self.allocations:
            raise ValueError("No allocations to export. Run allocation first.")
            
        data = {
            "allocations": self.allocations,
            "project_stats": self.get_project_stats()
        }
        with open(file_path, mode='w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def export_markdown_report(self, file_path: Path):
        """Exports a beautiful markdown report of the project distribution."""
        if not self.allocations:
            raise ValueError("No allocations to export. Run allocation first.")
            
        stats = self.get_project_stats()
        
        md_lines = [
            "# Capstone Project Allocation Report",
            "",
            "This report lists the results of the random lot-based drawing for the AI-Driven Engineering Capstone Projects.",
            "",
            "## Summary of Assignments",
            "",
            "| Team / Student Name | Allocated Project | Stream | Paradigm |",
            "| :--- | :--- | :--- | :--- |"
        ]
        
        for team, proj in sorted(self.allocations.items()):
            md_lines.append(f"| **{team}** | {proj['id']}. {proj['title']} | {proj['stream']} | `{proj['paradigm']}` |")
            
        md_lines.extend([
            "",
            "## Distribution Statistics",
            "",
            "| Project ID | Project Title | Engineering Stream | Assigned Teams | Count |",
            "| :---: | :--- | :--- | :--- | :---: |"
        ])
        
        for proj in self.projects:
            assigned_teams = stats.get(proj["id"], [])
            teams_str = ", ".join(f"**{t}**" for t in assigned_teams) if assigned_teams else "*None assigned*"
            md_lines.append(f"| {proj['id']} | {proj['title']} | {proj['stream']} | {teams_str} | {len(assigned_teams)} |")
            
        md_lines.extend([
            "",
            "---",
            "*Report generated automatically by the Capstone Project Lot Allocator.*"
        ])
        
        with open(file_path, mode='w', encoding='utf-8') as f:
            f.write("\n".join(md_lines))
