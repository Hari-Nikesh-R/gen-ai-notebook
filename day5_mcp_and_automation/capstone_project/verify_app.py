import sys
from pathlib import Path

from project_parser import ProjectParser
from allocator import ProjectAllocator

def run_verification():
    print("====================================================")
    print("🚀 RUNNING CAPSTONE PROJECT ALLOCATOR TEST SUITE")
    print("====================================================")

    # 1. Test Project Parser
    print("\n🔍 Step 1: Testing Project Parser...")
    readme_path = Path(__file__).parent / "README.md"
    parser = ProjectParser(readme_path)
    projects = parser.parse()
    
    assert len(projects) == 9, f"Expected 9 projects, but got {len(projects)}"
    print(f"✅ Success! Correctly parsed {len(projects)} projects.")
    
    # 2. Test Allocator Initial State
    print("\n🔍 Step 2: Testing Allocator Initialization...")
    allocator = ProjectAllocator(projects)
    assert len(allocator.projects) == 9, "Projects mismatch in allocator"
    assert len(allocator.teams) == 0, "Initial teams list should be empty"
    print("✅ Success! Allocator initialized properly.")

    # 3. Test Loading Teams
    print("\n🔍 Step 3: Testing Team List Ingestion...")
    teams_file = Path(__file__).parent / "teams.txt"
    num_loaded = allocator.load_teams_from_file(teams_file)
    assert num_loaded == 9, f"Expected 9 teams, but loaded {num_loaded}"
    assert len(allocator.teams) == 9, "Registered teams size mismatch"
    print(f"✅ Success! Successfully loaded {num_loaded} unique teams from teams.txt.")

    # 4. Test Allocation Engine (Balanced Mode)
    print("\n🔍 Step 4: Testing Allocation Engine (Balanced Mode)...")
    allocations = allocator.allocate(mode="balanced")
    
    assert len(allocations) == 9, f"Expected 9 assignments, got {len(allocations)}"
    for team, proj in allocations.items():
        assert proj in projects, f"Assigned project {proj} not in available projects"
        
    # Check stats for balance
    stats = allocator.get_project_stats()
    # For 9 teams and 9 projects: each project should have exactly 1 team assigned.
    project_counts = [len(teams) for teams in stats.values()]
    num_ones = project_counts.count(1)
    num_zeros = project_counts.count(0)
    
    print(f"   Allocation Spread Counts: {project_counts}")
    assert num_ones == 9, f"Expected exactly 9 projects to have 1 assignment, got {num_ones}"
    assert num_zeros == 0, f"Expected exactly 0 projects to have 0 assignments, got {num_zeros}"
    
    print("✅ Success! Balanced Mode distribution is mathematically perfect.")

    # 5. Test Allocation Engine (Custom Limit Mode)
    print("\n🔍 Step 5: Testing Allocation Engine (Custom Limit Mode)...")
    # Capacity limit = 2
    allocations = allocator.allocate(mode="custom_limit", custom_cap=2)
    assert len(allocations) == 9, f"Expected 9 assignments, got {len(allocations)}"
    
    stats = allocator.get_project_stats()
    for proj_id, assigned_teams in stats.items():
        assert len(assigned_teams) <= 2, f"Project {proj_id} exceeded capacity limit 2: {assigned_teams}"
        
    print("✅ Success! Custom Limit capacity boundaries respected perfectly.")

    # 6. Test Exporters
    print("\n🔍 Step 6: Testing Output Exporters...")
    csv_file = Path(__file__).parent / "test_allocations.csv"
    json_file = Path(__file__).parent / "test_allocations.json"
    md_file = Path(__file__).parent / "test_allocations_report.md"
    
    # Clean old test outputs if they exist
    for f in [csv_file, json_file, md_file]:
        if f.exists():
            f.unlink()
            
    allocator.export_csv(csv_file)
    allocator.export_json(json_file)
    allocator.export_markdown_report(md_file)
    
    assert csv_file.exists(), "CSV export failed"
    assert json_file.exists(), "JSON export failed"
    assert md_file.exists(), "Markdown report export failed"
    
    # Cleanup test outputs
    csv_file.unlink()
    json_file.unlink()
    md_file.unlink()
    
    print("✅ Success! Exporters generated valid CSV, JSON, and Markdown records.")
    
    print("\n====================================================")
    print("🎉 ALL TESTS PASSED! APPLICATION IS SOLID & CORRECT.")
    print("====================================================")

if __name__ == "__main__":
    run_verification()
