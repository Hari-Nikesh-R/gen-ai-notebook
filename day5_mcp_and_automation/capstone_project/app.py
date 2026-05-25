import os
import sys
import time
import random
from pathlib import Path
from typing import List, Dict, Any

# Ensure dependencies are loaded
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.prompt import Prompt, Confirm
    from rich.live import Live
    from rich.spinner import Spinner
    from rich.columns import Columns
    from rich.box import ROUNDED, HEAVY
    from rich.align import Align
except ImportError:
    print("Error: The 'rich' library is required to run this app.")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)

# Import local modules
from project_parser import ProjectParser
from allocator import ProjectAllocator

# Initialize Rich Console
console = Console()

class LotAllocatorApp:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.readme_path = self.base_dir / "README.md"
        
        # Parse projects
        try:
            self.parser = ProjectParser(self.readme_path)
            self.projects = self.parser.parse()
        except Exception as e:
            console.print(f"[bold red]Error loading projects from README.md:[/bold red] {e}")
            self.projects = []
            
        self.allocator = ProjectAllocator(self.projects)
        
        # Load default teams if available
        self.default_teams_path = self.base_dir / "teams.txt"
        if self.default_teams_path.exists():
            self.allocator.load_teams_from_file(self.default_teams_path)

    def print_banner(self):
        """Displays the application's premium title banner."""
        banner_text = Text()
        banner_text.append("🎲 CAPSTONE PROJECT LOT-BASED ALLOCATOR 🎲\n", style="bold gold1")
        banner_text.append("AI-Driven Engineering Capstone Assignments Generator", style="italic deep_sky_blue1")
        
        banner_panel = Panel(
            Align.center(banner_text),
            box=HEAVY,
            style="bold light_steel_blue",
            border_style="cyan"
        )
        console.print(banner_panel)

    def print_stats(self):
        """Prints high-level stats of projects, teams, and allocations."""
        num_projects = len(self.projects)
        num_teams = len(self.allocator.teams)
        num_allocations = len(self.allocator.allocations)
        
        status_text = Text()
        status_text.append("📚 Available Projects: ", style="bold")
        status_text.append(f"{num_projects}\n", style="bold cyan")
        
        status_text.append("👥 Registered Teams/Students: ", style="bold")
        status_text.append(f"{num_teams}\n", style="bold magenta")
        
        status_text.append("⚙️ Allocation Status: ", style="bold")
        if num_allocations > 0:
            status_text.append("Allocated ✅", style="bold green")
        elif num_teams > 0:
            status_text.append("Ready to Draw Lots ⏳", style="bold yellow")
        else:
            status_text.append("Awaiting Teams ❌", style="bold red")
            
        stats_panel = Panel(
            status_text,
            title="System Status",
            title_align="left",
            box=ROUNDED,
            border_style="grey50"
        )
        console.print(stats_panel)

    def display_projects(self):
        """Displays all projects in a beautiful, structured table."""
        if not self.projects:
            console.print("[bold red]No projects parsed yet![/bold red]")
            return
            
        table = Table(
            title="🎯 Available Capstone Projects",
            title_style="bold gold1",
            box=ROUNDED,
            border_style="cyan",
            show_header=True,
            header_style="bold deep_sky_blue1"
        )
        
        table.add_column("ID", style="bold white", width=4, justify="center")
        table.add_column("Project Title", style="bold green", ratio=3)
        table.add_column("Engineering Stream", style="magenta", ratio=2)
        table.add_column("AI Paradigm", style="cyan", ratio=2)
        table.add_column("Difficulty", style="bold yellow", width=15)
        
        for p in self.projects:
            # Shorten stream / paradigm if too long
            stream = p["stream"]
            if len(stream) > 40:
                stream = stream[:37] + "..."
            table.add_row(
                str(p["id"]),
                p["title"],
                stream,
                p["paradigm"],
                p["difficulty"]
            )
            
        console.print(table)

    def display_teams(self):
        """Displays currently loaded teams."""
        if not self.allocator.teams:
            console.print("[bold yellow]No teams currently registered.[/bold yellow]")
            return
            
        table = Table(
            title="👥 Registered Teams/Students",
            title_style="bold magenta",
            box=ROUNDED,
            border_style="magenta",
            show_header=True,
            header_style="bold white"
        )
        table.add_column("Index", style="cyan", justify="center", width=6)
        table.add_column("Team/Student Name", style="bold white")
        table.add_column("Allocated Project", style="bold green")
        
        for idx, team in enumerate(self.allocator.teams, 1):
            allocated_project = "Not assigned yet"
            if team in self.allocator.allocations:
                proj = self.allocator.allocations[team]
                allocated_project = f"{proj['id']}. {proj['title']}"
            table.add_row(str(idx), team, allocated_project)
            
        console.print(table)

    def load_teams(self):
        """Interactive prompt to load teams from a file."""
        console.print("\n[bold cyan]📂 Load Teams/Students List[/bold cyan]")
        console.print("You can load from a simple text file (one name per line) or a CSV file.")
        
        default_path = str(self.default_teams_path.relative_to(self.base_dir))
        file_path_str = Prompt.ask(
            "Enter path to teams file", 
            default=default_path
        )
        
        file_path = Path(file_path_str)
        # If absolute path, or relative to cwd/base_dir
        if not file_path.exists():
            # Try relative to base_dir
            file_path = self.base_dir / file_path_str
            
        if not file_path.exists():
            console.print(f"[bold red]File not found at: {file_path_str}[/bold red]")
            return
            
        try:
            count = self.allocator.load_teams_from_file(file_path)
            console.print(f"[bold green]Successfully loaded {count} unique teams from {file_path.name}![/bold green]")
        except Exception as e:
            console.print(f"[bold red]Failed to load teams:[/bold red] {e}")

    def add_team_manually(self):
        """Allows manual registration of teams."""
        console.print("\n[bold cyan]➕ Add Team Manually[/bold cyan]")
        team_name = Prompt.ask("Enter student or team name")
        if not team_name.strip():
            console.print("[bold red]Invalid name![/bold red]")
            return
            
        current_teams = self.allocator.teams
        if team_name.strip() in current_teams:
            console.print(f"[bold yellow]'{team_name}' is already registered.[/bold yellow]")
            return
            
        current_teams.append(team_name.strip())
        self.allocator.set_teams(current_teams)
        console.print(f"[bold green]Team '{team_name}' registered successfully![/bold green]")

    def run_lottery_draw(self):
        """Runs the main lot-based project allocation drawing with beautiful animations!"""
        if not self.allocator.teams:
            console.print("[bold red]Error: Please load or add teams first.[/bold red]")
            return
            
        console.print("\n[bold gold1]🎲 CAPSTONE DRAW-OF-LOTS CONFIGURATION[/bold gold1]")
        
        # Prompt for allocation mode
        mode_choice = Prompt.ask(
            "Select Allocation Mode", 
            choices=["balanced", "custom_limit"], 
            default="balanced"
        )
        
        custom_cap = None
        if mode_choice == "custom_limit":
            min_cap = (len(self.allocator.teams) + len(self.projects) - 1) // len(self.projects)
            console.print(f"[dim]Note: Since there are {len(self.allocator.teams)} teams and {len(self.projects)} projects, minimum capacity per project is {min_cap}.[/dim]")
            
            cap_str = Prompt.ask(
                "Enter maximum capacity limit per project",
                default=str(min_cap)
            )
            try:
                custom_cap = int(cap_str)
                if custom_cap < min_cap:
                    console.print(f"[bold red]Capacity limit must be at least {min_cap}.[/bold red]")
                    return
            except ValueError:
                console.print("[bold red]Invalid capacity value. Must be an integer.[/bold red]")
                return

        animate = Confirm.ask("Do you want to run the lottery with a suspenseful drawing animation?", default=True)
        
        console.print("\n[bold gold1]⚙️ Allocating projects...[/bold gold1]\n")
        
        try:
            allocations = self.allocator.allocate(mode=mode_choice, custom_cap=custom_cap)
        except Exception as e:
            console.print(f"[bold red]Allocation failed:[/bold red] {e}")
            return
            
        if animate:
            # We animate the drawing for each team one-by-one!
            console.print("[bold cyan]🔮 Initiating Random Draw...[/bold cyan]")
            time.sleep(1.0)
            
            shuffled_teams = list(allocations.keys())
            # Maintain the shuffled draw order for realism!
            
            for index, team in enumerate(shuffled_teams, 1):
                project = allocations[team]
                
                # Create a Live component to show an exciting roulette spin
                spin_chars = ["◜", "◠", "◝", "◞", "◡", "◟"]
                animation_duration = 1.2 # seconds
                start_time = time.time()
                
                with Live(
                    Spinner("dots", text=Text(f"Drawing project for {team}...", style="bold magenta")), 
                    console=console, 
                    transient=True
                ) as live:
                    while time.time() - start_time < animation_duration:
                        # Pick a random project to show in the spinner as a roulette effect!
                        fake_proj = random.choice(self.projects)
                        live.update(
                            Panel(
                                Text(f"🎲 Drawing lot for: {team}\n🌀 Shuffling lots: {fake_proj['title']}", style="bold cyan"),
                                border_style="yellow",
                                box=ROUNDED
                            )
                        )
                        time.sleep(0.08)
                
                # Draw complete! Print the final allocation beautifully
                outcome_text = Text()
                outcome_text.append(f"[{index}/{len(shuffled_teams)}] ", style="dim")
                outcome_text.append(f"👤 {team:<18} Assigned ➜ ", style="bold white")
                outcome_text.append(f"[{project['id']}] {project['title']}", style="bold green")
                outcome_text.append(f" ({project['stream']})", style="italic cyan")
                
                console.print(outcome_text)
                time.sleep(0.4) # Brief pause before next team
                
            console.print("\n[bold green]🏆 Draw-of-lots completed successfully![/bold green]\n")
        else:
            # Immediate assignment printout
            console.print("[bold green]Allocation complete! Showing assignments:[/bold green]")
            self.display_teams()

    def export_allocations(self):
        """Exports the allocations in all supported formats."""
        if not self.allocator.allocations:
            console.print("[bold red]No allocations to export. Please run a lottery draw first.[/bold red]")
            return
            
        console.print("\n[bold cyan]💾 Exporting Allocations[/bold cyan]")
        
        csv_path = self.base_dir / "allocations.csv"
        json_path = self.base_dir / "allocations.json"
        md_path = self.base_dir / "allocations_report.md"
        
        try:
            self.allocator.export_csv(csv_path)
            self.allocator.export_json(json_path)
            self.allocator.export_markdown_report(md_path)
            
            console.print(f"[bold green]✓ CSV report successfully saved to:[/bold green] {csv_path.name}")
            console.print(f"[bold green]✓ JSON file successfully saved to:[/bold green] {json_path.name}")
            console.print(f"[bold green]✓ Markdown report successfully saved to:[/bold green] {md_path.name}")
            console.print("\n[bold yellow]💡 Tip:[/bold yellow] You can check [allocations_report.md](file:///" + str(md_path) + ") to view the fully formatted allocations markdown document!")
        except Exception as e:
            console.print(f"[bold red]Failed to export reports:[/bold red] {e}")

    def reset_allocations(self):
        """Clears all assignments."""
        if not self.allocator.allocations:
            console.print("[bold yellow]No assignments to reset.[/bold yellow]")
            return
            
        confirm = Confirm.ask("[bold red]Are you sure you want to reset and clear all current assignments?[/bold red]")
        if confirm:
            self.allocator.allocations = {}
            console.print("[bold green]Assignments cleared.[/bold green]")

    def run(self):
        """Main application execution loop."""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            self.print_banner()
            self.print_stats()
            
            console.print("\n[bold underline cyan]Available Operations:[/bold underline cyan]")
            console.print(" 1. View Capstone Projects List")
            console.print(" 2. Load Teams/Students List from File")
            console.print(" 3. Add a Single Team/Student Manually")
            console.print(" 4. View Current Teams & Allocations Table")
            console.print(" 5. Run Random Draw-of-Lots (Lottery Assignment)")
            console.print(" 6. Export Assignments to CSV, JSON & Markdown Report")
            console.print(" 7. Reset Current Assignments")
            console.print(" 8. Exit")
            
            choice = Prompt.ask("\nSelect an option", choices=[str(i) for i in range(1, 9)], default="5")
            
            if choice == "1":
                self.display_projects()
                Prompt.ask("\nPress Enter to return to main menu")
            elif choice == "2":
                self.load_teams()
                Prompt.ask("\nPress Enter to return to main menu")
            elif choice == "3":
                self.add_team_manually()
                Prompt.ask("\nPress Enter to return to main menu")
            elif choice == "4":
                self.display_teams()
                Prompt.ask("\nPress Enter to return to main menu")
            elif choice == "5":
                self.run_lottery_draw()
                Prompt.ask("\nPress Enter to return to main menu")
            elif choice == "6":
                self.export_allocations()
                Prompt.ask("\nPress Enter to return to main menu")
            elif choice == "7":
                self.reset_allocations()
                Prompt.ask("\nPress Enter to return to main menu")
            elif choice == "8":
                console.print("\n[bold gold1]Thank you for using Capstone Project Allocator! Good luck with your projects! ✨[/bold gold1]")
                break

if __name__ == "__main__":
    app = LotAllocatorApp()
    app.run()
