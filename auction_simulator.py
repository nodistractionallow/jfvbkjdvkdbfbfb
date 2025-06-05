import pandas as pd
import random
import time
import json
from colorama import init, Fore, Style
import traceback

# Initialize colorama for colored output
init()

# Complete name mapping for all 88 players
NAME_MAPPING = {
    "Ravindra Jadeja": "RA Jadeja",
    "Yashasvi Jaiswal": "YBK Jaiswal",
    "Deepak Chahar": "DL Chahar",
    "Ambati Rayudu": "AT Rayudu",
    "Moeen Ali": "MM Ali",
    "MS Dhoni": "MS Dhoni",
    "Suresh Raina": "SK Raina",
    "Sam Curran": "SM Curran",
    "Rishabh Pant": "RR Pant",
    "Axar Patel": "AR Patel",
    "Prithvi Shaw": "PP Shaw",
    "Shikhar Dhawan": "S Dhawan",
    "Anrich Nortje": "A Nortje",
    "Kagiso Rabada": "K Rabada",
    "Shreyas Iyer": "SS Iyer",
    "Avesh Khan": "Avesh Khan",
    "Andre Russell": "AD Russell",
    "Sunil Narine": "SP Narine",
    "Nitish Rana": "N Rana",
    "Eoin Morgan": "EJG Morgan",
    "Varun Chakravarthy": "CV Varun",
    "Shivam Mavi": "Shivam Mavi",
    "Shahrukh Khan": "M Shahrukh Khan",
    "Dinesh Karthik": "KD Karthik",
    "Rohit Sharma": "RG Sharma",
    "Jasprit Bumrah": "JJ Bumrah",
    "Suryakumar Yadav": "SA Yadav",
    "Kieron Pollard": "KA Pollard",
    "Hardik Pandya": "HH Pandya",
    "Ishan Kishan": "Ishan Kishan",
    "Krunal Pandya": "KH Pandya",
    "Rahul Chahar": "RD Chahar",
    "KL Rahul": "KL Rahul",
    "Chris Gayle": "CH Gayle",
    "Mayank Agarwal": "MA Agarwal",
    "Mohammed Shami": "Mohammed Shami",
    "Arshdeep Singh": "Arshdeep Singh",
    "Harpreet Brar": "Harpreet Brar",
    "Nicholas Pooran": "N Pooran",
    "Ravi Bishnoi": "Ravi Bishnoi",
    "Virat Kohli": "V Kohli",
    "AB de Villiers": "AB de Villiers",
    "Devdutt Padikkal": "D Padikkal",
    "Glenn Maxwell": "GJ Maxwell",
    "Mohammed Siraj": "Mohammed Siraj",
    "Yuzvendra Chahal": "YS Chahal",
    "Harshal Patel": "HV Patel",
    "Shahbaz Ahmed": "Shahbaz Ahmed",
    "Sanju Samson": "SV Samson",
    "Jos Buttler": "JC Buttler",
    "Ben Stokes": "Ben Stokes",
    "Jofra Archer": "Jofra Archer",
    "Rahul Tewatia": "R Tewatia",
    "Riyan Parag": "R Parag",
    "Chris Morris": "CH Morris",
    "Kartik Tyagi": "Kartik Tyagi",
    "Kane Williamson": "KS Williamson",
    "David Warner": "DA Warner",
    "Rashid Khan": "Rashid Khan",
    "Bhuvneshwar Kumar": "B Kumar",
    "Jonny Bairstow": "JM Bairstow",
    "Manish Pandey": "MK Pandey",
    "Vijay Shankar": "V Shankar",
    "Abdul Samad": "Abdul Samad",
    "Faf du Plessis": "F du Plessis",
    "Liam Livingstone": "LS Livingstone",
    "Quinton de Kock": "Q de Kock",
    "Ravichandran Ashwin": "R Ashwin",
    "Wriddhiman Saha": "WP Saha",
    "Lalit Yadav": "Lalit Yadav",
    "Dan Christian": "DT Christian",
    "Khaleel Ahmed": "KK Ahmed",
    "David Miller": "DA Miller",
    "Trent Boult": "TA Boult",
    "Mahipal Lomror": "MK Lomror",
    "Adam Milne": "AF Milne",
    "Kedar Jadhav": "KM Jadhav",
    "Deepak Hooda": "DJ Hooda",
    "Shimron Hetmyer": "SO Hetmyer",
    "Navdeep Saini": "NA Saini",
    "Dwayne Bravo": "DJ Bravo",
    "Nathan Ellis": "Nathan Ellis",
    "Chetan Sakariya": "C Sakariya",
    "Mustafizur Rahman": "Mustafizur Rahman",
    "Washington Sundar": "Washington Sundar",
    "Shardul Thakur": "SN Thakur",
    "Rinku Singh": "Rinku Singh",
    "Tilak Verma": "Tilak Verma",
    "Lockie Ferguson": "Lockie Ferguson"
}

# -------------------- Load Data --------------------
def load_stats(filepath):
    """Load player statistics from a text file into a pandas DataFrame."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            lines = file.readlines()
        headers = [h.strip() for h in lines[1].split("|")[1:-1]]
        data = [[col.strip() for col in line.split("|")[1:-1]] for line in lines[3:-1]]
        df = pd.DataFrame(data, columns=headers)
        if "Player" in df.columns:
            df["Player"] = df["Player"].astype(str).str.strip()
        else:
            print(f"{Fore.RED}Error: 'Player' column not found in {filepath}{Style.RESET_ALL}")
            return pd.DataFrame()
        print(f"{Fore.YELLOW}Debug: {filepath} columns: {df.columns.tolist()}{Style.RESET_ALL}")
        return df
    except Exception as e:
        print(f"{Fore.RED}Error loading {filepath}: {e}{Style.RESET_ALL}")
        return pd.DataFrame()

def load_teams(filepath):
    """Load team rosters from teams.json."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            teams = json.load(file)
        return teams
    except Exception as e:
        print(f"{Fore.RED}Error loading {filepath}: {e}{Style.RESET_ALL}")
        return {}

bat = load_stats("batStats.txt")
bowl = load_stats("bowlStats.txt")
teams_data = load_teams("teams.json")

if bat.empty or bowl.empty or not teams_data:
    print(f"{Fore.RED}Failed to load required data. Exiting game.{Style.RESET_ALL}")
    exit()

# Convert numeric columns
bat['Runs'] = pd.to_numeric(bat['Runs'], errors='coerce').fillna(0).astype(int)
bat['Average'] = pd.to_numeric(bat['Average'], errors='coerce').fillna(0)
bat['SR'] = pd.to_numeric(bat['SR'], errors='coerce').fillna(0)
bowl['Wickets'] = pd.to_numeric(bowl['Wickets'], errors='coerce').fillna(0).astype(int)
bowl['Economy'] = pd.to_numeric(bowl['Economy'], errors='coerce').fillna(0)

# Ensure Player column is string
bat['Player'] = bat['Player'].astype(str).str.strip()
bowl['Player'] = bowl['Player'].astype(str).str.strip()

# Merge batting and bowling stats
merged = pd.merge(bat, bowl, on='Player', how='outer', suffixes=('_bat', '_bowl')).fillna(0)
print(f"{Fore.YELLOW}Debug: Merged DataFrame columns: {merged.columns.tolist()}{Style.RESET_ALL}")
print(f"{Fore.YELLOW}Debug: First few players: {merged['Player'].head().tolist()}{Style.RESET_ALL}")

# Validate Player column
if not merged['Player'].apply(lambda x: isinstance(x, str)).all():
    print(f"{Fore.RED}Warning: Non-string values in Player column. Cleaning data.{Style.RESET_ALL}")
    merged['Player'] = merged['Player'].astype(str).str.strip()
    merged = merged[merged['Player'].str.len() > 0]

# -------------------- Player Setup --------------------
def get_role(runs, wickets, player_name):
    """Determine player role based on stats and name."""
    wicketkeepers = ['RR Pant', 'Q de Kock', 'SV Samson', 'Ishan Kishan', 'WP Saha', 'MS Dhoni', 'D Padikkal']
    mapped_name = NAME_MAPPING.get(player_name, player_name)
    if mapped_name in wicketkeepers:
        return "Wicketkeeper-Batter"
    if runs > 100 and wickets > 5:
        return "All-Rounder"
    elif runs > 100:
        return "Batter"
    elif wickets > 5:
        return "Bowler"
    return "All-Rounder" if wickets > 0 else "Batter"

# Create auction pool from teams.json
auction_pool = []
player_names = set()
for team, players in teams_data.items():
    for player_name in players:
        if not isinstance(player_name, str) or not player_name or player_name in player_names:
            print(f"{Fore.YELLOW}Skipping invalid or duplicate player: {player_name}{Style.RESET_ALL}")
            continue
        player_names.add(player_name)
        stats_name = NAME_MAPPING.get(player_name, player_name)
        stats = merged[merged['Player'] == stats_name]
        runs = int(stats['Runs'].iloc[0]) if not stats.empty and 'Runs' in stats.columns else 0
        wickets = int(stats['Wickets'].iloc[0]) if not stats.empty and 'Wickets' in stats.columns else 0
        avg = stats['Average'].iloc[0] if not stats.empty and 'Average' in stats.columns else "NA"
        eco = stats['Economy'].iloc[0] if not stats.empty and 'Economy' in stats.columns else "NA"
        sr = stats['SR'].iloc[0] if not stats.empty and 'SR' in stats.columns else 0
        demand = (runs / 10 + wickets * 5 + sr / 5) if sr > 0 else (runs / 10 + wickets * 5)
        base_price = max(20, min(200, int(demand / 4)))  # Adjusted for 2000L budget
        player = {
            "name": player_name,
            "runs": runs,
            "wickets": wickets,
            "avg": avg,
            "eco": eco,
            "base_price": base_price,
            "demand": int(demand),
            "role": get_role(runs, wickets, player_name)
        }
        auction_pool.append(player)

print(f"{Fore.YELLOW}Debug: Auction pool size before retention: {len(auction_pool)} players{Style.RESET_ALL}")

# -------------------- Game Setup --------------------
class Team:
    def __init__(self, name):
        self.name = name
        self.squad = []
        self.budget = 2000  # Budget set to 2000L
        self.max_squad_size = 11
        self.min_batters = 4
        self.min_bowlers = 4
        self.min_wicketkeepers = 1
        self.min_allrounders = 2

    def can_add_player(self, role):
        """Check if team can add a player based on squad size."""
        return len(self.squad) < self.max_squad_size

    def needs_role(self, role):
        """Check if team needs a specific role."""
        batters = sum(1 for p in self.squad if "Batter" in p["role"])
        bowlers = sum(1 for p in self.squad if p["role"] == "Bowler")
        wicketkeepers = sum(1 for p in self.squad if "Wicketkeeper" in p["role"])
        allrounders = sum(1 for p in self.squad if p["role"] == "All-Rounder")
        if role == "Batter" and batters < self.min_batters:
            return 3.0
        if role == "Bowler" and bowlers < self.min_bowlers:
            return 3.0
        if role == "Wicketkeeper-Batter" and wicketkeepers < self.min_wicketkeepers:
            return 3.0
        if role == "All-Rounder" and allrounders < self.min_allrounders:
            return 3.0
        return 1.0

class Auction:
    def __init__(self):
        self.teams = [Team(name.upper()) for name in teams_data.keys()]
        self.user_team = None
        self.auction_pool = auction_pool
        self.sold_players = []
        self.current_index = 0
        self.autosim_speed = None

    def retain_players(self, team_name, num_retain, is_user=False):
        """Retain players based on stats with a flat 150L fee."""
        team = next(t for t in self.teams if t.name == team_name)
        original_roster = teams_data.get(team_name.lower(), [])
        if not original_roster:
            print(f"{Fore.RED}No players found for {team_name} in teams.json{Style.RESET_ALL}")
            return
        
        # Create player list with stats
        roster_with_stats = []
        for player_name in original_roster:
            player = next((p for p in self.auction_pool if p["name"] == player_name), None)
            if player:
                roster_with_stats.append(player)
        
        # Sort by demand score
        roster_with_stats.sort(key=lambda p: p["demand"], reverse=True)
        
        if is_user:
            print(f"\n{Fore.CYAN}Available players for {team_name} (sorted by demand):{Style.RESET_ALL}")
            for i, player in enumerate(roster_with_stats, 1):
                print(f"{i}. {player['name']} - {player['role']} - {player['runs']} Runs, {player['wickets']} Wickets, Demand: {player['demand']}")
            retained = []
            for i in range(num_retain):
                while True:
                    try:
                        choice = int(input(f"Enter player number {i+1} to retain (1-{len(roster_with_stats)}): "))
                        if 1 <= choice <= len(roster_with_stats) and roster_with_stats[choice-1]["name"] not in retained:
                            retained.append(roster_with_stats[choice-1]["name"])
                            break
                        print(f"{Fore.RED}Invalid or already retained player. Try again.{Style.RESET_ALL}")
                    except ValueError:
                        print(f"{Fore.RED}Enter a valid number.{Style.RESET_ALL}")
        else:
            retained = [p["name"] for p in roster_with_stats[:min(num_retain, len(roster_with_stats))]]
        
        for player_name in retained:
            player = next((p for p in self.auction_pool if p["name"] == player_name), None)
            if player:
                retain_price = 150  # Flat 150L fee
                if team.budget >= retain_price:
                    team.squad.append({**player, "Price": retain_price})
                    team.budget -= retain_price
                    self.auction_pool.remove(player)
                    print(f"{team_name} retains {player_name} for ₹{retain_price}L")
                else:
                    print(f"{Fore.YELLOW}{team_name} cannot afford to retain {player_name}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}Player {player_name} not found in auction pool{Style.RESET_ALL}")

    def show_dashboard(self):
        """Display auction status."""
        batters = sum(1 for p in self.user_team.squad if "Batter" in p["role"])
        bowlers = sum(1 for p in self.user_team.squad if p["role"] == "Bowler")
        wicketkeepers = sum(1 for p in self.user_team.squad if "Wicketkeeper" in p["role"])
        allrounders = sum(1 for p in self.user_team.squad if p["role"] == "All-Rounder")
        print(f"\n{Fore.CYAN}=== Franchise Dashboard: {self.user_team.name} ==={Style.RESET_ALL}")
        print(f"Budget: ₹{self.user_team.budget}L | Squad: {len(self.user_team.squad)}/{self.user_team.max_squad_size}")
        print(f"Composition: Batters: {batters}/{self.user_team.min_batters}, Bowlers: {bowlers}/{self.user_team.min_bowlers}, WKs: {wicketkeepers}/{self.user_team.min_wicketkeepers}, ARs: {allrounders}/{self.user_team.min_allrounders}")
        print(f"Players Remaining: {len(self.auction_pool) - self.current_index}")
        print(f"Squad: {[f'{p['name']} (₹{p['Price']}L)' for p in self.user_team.squad]}")
        print(f"{Fore.CYAN}====================================={Style.RESET_ALL}")

    def show_team_budgets(self):
        """Display all teams' remaining budgets."""
        print(f"\n{Fore.YELLOW}=== Team Budgets ==={Style.RESET_ALL}")
        for team in sorted(self.teams, key=lambda t: t.budget, reverse=True):
            print(f"{team.name}: ₹{team.budget}L ({len(team.squad)}/{team.max_squad_size} players)")
        print(f"{Fore.YELLOW}==================={Style.RESET_ALL}")

    def show_player(self, player):
        """Display player profile."""
        print(f"\n{Fore.YELLOW}--- Player Profile: {player['name']} ---{Style.RESET_ALL}")
        print(f"🏏 Role: {player['role']}")
        print(f"📊 Batting: {player['runs']} runs, Avg: {player['avg']}")
        print(f"🏈 Bowling: {player['wickets']} wickets, Eco: {player['eco']}")
        print(f"💰 Base Price: ₹{player['base_price']}L | Demand Score: {player['demand']}")

    def simulate_bidding(self, player, user_participates=False, autosimulate=False, action=""):
        """Simulate strategic bidding with real IPL owner tactics."""
        price = player["base_price"]
        current_winner = None
        early_auction = self.current_index < len(self.auction_pool) * 0.2  # First 20% (~17 players)
        late_auction = sum(1 for t in self.teams if len(t.squad) < 10) >= 4
        bid_step = random.choice([10, 20, 50, 100]) if player["demand"] > 200 else random.choice([10, 20])
        max_bids = random.randint(20, 30) if player["demand"] > 200 and late_auction else random.randint(10, 20)
        dropout_rate = 0.03 if player["demand"] > 200 and late_auction else 0.05
        if late_auction and player["demand"] > 200:
            print(f"{Fore.RED}It's a fierce battle for {player['name']} as budgets dwindle!{Style.RESET_ALL}")

        # Ensure at least 4 teams initially
        teams_in_auction = [
            t for t in self.teams
            if t.budget >= price * 0.8 and t.can_add_player(player["role"]) and (t.name != self.user_team.name or user_participates)
        ]
        teams_in_auction.sort(key=lambda t: -t.budget)  # Prioritize high-budget teams
        if len(teams_in_auction) < 4 and teams_in_auction:
            extra_teams = [
                t for t in self.teams
                if t not in teams_in_auction and t.can_add_player(player["role"]) and t.budget >= price * 0.5
            ]
            extra_teams.sort(key=lambda t: -t.budget)
            teams_in_auction.extend(extra_teams[:4 - len(teams_in_auction)])

        print(f"{Fore.YELLOW}Debug: Teams in auction for {player['name']}: {[t.name for t in teams_in_auction]}{Style.RESET_ALL}")

        # Competitive bidding with real IPL strategies
        bid_count = 0
        prev_bidder = None
        while bid_count < max_bids and len(teams_in_auction) > 1:
            bid_count += 1
            teams_in_auction = [t for t in teams_in_auction if random.random() > dropout_rate or t.needs_role(player["role"]) > 1.5]
            if len(teams_in_auction) <= 1:
                break
            eligible_bidders = [t for t in teams_in_auction if t != prev_bidder]
            if not eligible_bidders:
                eligible_bidders = teams_in_auction
            # Strategic bidding weights
            weights = []
            for t in eligible_bidders:
                weight = t.needs_role(player["role"]) * (1 + t.budget / 2000)
                remaining_players = 11 - len(t.squad)
                # Marquee targeting (early auction, high-demand)
                if early_auction and player["demand"] > 300 and t.budget > 1500:
                    weight *= 2.0
                    print(f"{Fore.MAGENTA}{t.name} targets marquee player {player['name']}!{Style.RESET_ALL}")
                # Budget pacing
                max_bid = t.budget * 0.6 if self.current_index < len(self.auction_pool) * 0.5 else (t.budget // remaining_players) * 1.5
                # Opportunistic bargains (late auction, low-demand)
                if self.current_index > len(self.auction_pool) * 0.7 and player["demand"] < 100:
                    weight *= 2.0 if t.budget < 700 else 1.0
                    bid_step = random.choice([10, 20])
                # Avoid overpayment
                if price > t.budget * 0.25 and t.needs_role(player["role"]) < 2.0:
                    weight *= 0.2
                # Budget constraint for low-budget teams
                if t.budget < 700 and len(t.squad) < 6:
                    weight *= 3.0 if player["demand"] < 100 else 0.3
                    if price + bid_step > max_bid:
                        weight *= 0.5
                weights.append(weight)
            bidder = random.choices(eligible_bidders, weights=weights, k=1)[0]
            if bidder.budget >= price + bid_step:
                if player["demand"] > 300 and random.random() < 0.15:
                    bid_step = random.choice([50, 75, 100])
                    print(f"{Fore.MAGENTA}{bidder.name} makes a bold bid!{Style.RESET_ALL}")
                price += bid_step
                current_winner = bidder
                prev_bidder = bidder
                print(f"{bidder.name} bids ₹{price}L")
                time.sleep(0.2 if autosimulate else 0.5)
            else:
                teams_in_auction.remove(bidder)

        # User bidding (for bid or observe mode)
        if (user_participates or action == "o") and self.user_team.can_add_player(player["role"]):
            if autosimulate:
                if player["demand"] > 150 and self.user_team.budget >= price + bid_step and random.random() < 0.8:
                    price += bid_step
                    current_winner = self.user_team
                    prev_bidder = self.user_team
                    print(f"{Fore.MAGENTA}{self.user_team.name} joins the fray with ₹{price}L!{Style.RESET_ALL}")
            else:
                while True:
                    try:
                        bid = input(f"\n➡️ Current bid ₹{price}L by {current_winner.name if current_winner else 'None'}. Your bid (or 'pass'): ")
                        if bid.lower() == "pass":
                            break
                        bid = int(bid)
                        if bid <= price:
                            print(f"{Fore.RED}Bid must exceed ₹{price}L.{Style.RESET_ALL}")
                            continue
                        if bid > self.user_team.budget:
                            print(f"{Fore.RED}Insufficient budget (₹{self.user_team.budget}L available).{Style.RESET_ALL}")
                            continue
                        price = bid
                        current_winner = self.user_team
                        prev_bidder = self.user_team
                        print(f"{Fore.MAGENTA}{self.user_team.name} raises the stakes to ₹{price}L!{Style.RESET_ALL}")
                        break
                    except ValueError:
                        print(f"{Fore.RED}Enter a number or 'pass'.{Style.RESET_ALL}")

        # Ensure player is sold
        if not current_winner:
            eligible_teams = [t for t in self.teams if t.budget >= player["base_price"] * 0.8 and t.can_add_player(player["role"])]
            eligible_teams.sort(key=lambda t: -t.budget)
            if eligible_teams:
                current_winner = eligible_teams[0]
                price = player["base_price"]
                print(f"{current_winner.name} secures {player['name']} at base price ₹{price}L")
            else:
                eligible_teams = [t for t in self.teams if len(t.squad) < t.max_squad_size]
                eligible_teams.sort(key=lambda t: -t.budget)
                if eligible_teams:
                    current_winner = eligible_teams[0]
                    price = max(10, player["base_price"] // 2)
                    print(f"{current_winner.name} assigned {player['name']} for ₹{price}L")

        if current_winner:
            current_winner.squad.append({**player, "Price": price})
            current_winner.budget -= price
            self.sold_players.append((player["name"], price, current_winner.name))
            print(f"{Fore.GREEN}🔨 Sold to {current_winner.name} for ₹{price}L{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Fatal Error: Failed to assign {player['name']}. Check squad sizes and budgets.{Style.RESET_ALL}")
            exit()

    def save_teams(self, filepath="teams.json"):
        """Save final team rosters to teams.json with debug logging."""
        teams = {t.name.lower(): [p["name"] for p in t.squad] for t in self.teams}
        print(f"{Fore.YELLOW}Debug: Attempting to save {len(teams)} teams to {filepath}{Style.RESET_ALL}")
        try:
            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(teams, file, indent=4)
            print(f"{Fore.GREEN}Team rosters saved to {filepath}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error saving {filepath}: {e}{Style.RESET_ALL}")
            print(f"{Fore.RED}Stack trace: {traceback.format_exc()}{Style.RESET_ALL}")

    def all_teams_full(self):
        """Check if all teams have reached max squad size."""
        return all(len(t.squad) >= t.max_squad_size for t in self.teams)

    def auction_summary(self):
        """Display auction summary with player and team analysis."""
        print(f"\n{Fore.CYAN}=== Auction Summary ==={Style.RESET_ALL}")
        # Player Analysis
        print(f"\n{Fore.YELLOW}Player Analysis:{Style.RESET_ALL}")
        top_purchases = sorted(self.sold_players, key=lambda x: x[1], reverse=True)[:5]
        print("Top 5 Purchases:")
        for player, price, team in top_purchases:
            p = next((p for p in auction_pool if p["name"] == player), None)
            if p:
                print(f"{player} ({p['role']}) - ₹{price}L to {team}")
        
        # Team Analysis
        print(f"\n{Fore.YELLOW}Team Analysis:{Style.RESET_ALL}")
        for team in self.teams:
            batters = sum(1 for p in team.squad if "Batter" in p["role"])
            bowlers = sum(1 for p in team.squad if p["role"] == "Bowler")
            wicketkeepers = sum(1 for p in team.squad if "Wicketkeeper" in p["role"])
            allrounders = sum(1 for p in team.squad if p["role"] == "All-Rounder")
            total_runs = sum(p["runs"] for p in team.squad)
            total_wickets = sum(p["wickets"] for p in team.squad)
            role_score = (min(batters, 4) + min(bowlers, 4) + min(wicketkeepers, 1) + min(allrounders, 2)) / 11 * 100
            rating = min(100, int((total_runs / 100 + total_wickets * 5 + role_score * 10) / 2))
            print(f"{team.name}: {len(team.squad)} players - Budget: ₹{team.budget}L")
            print(f"  Composition: {batters} Batters, {bowlers} Bowlers, {wicketkeepers} WKs, {allrounders} ARs")
            print(f"  Stats: {total_runs} Runs, {total_wickets} Wickets")
            print(f"  Strengths: {'Strong batting' if total_runs > 2000 else 'Balanced batting'}, {'Strong bowling' if total_wickets > 50 else 'Balanced bowling'}")
            print(f"  Team Rating: {rating}/100")

    def run(self):
        """Run the auction simulation."""
        print(f"{Fore.CYAN}🏏 IPL Auction Simulator 2025{Style.RESET_ALL}")
        print("Available Franchises:", ", ".join(t.name for t in self.teams))
        team_name = input("Choose your franchise: ").strip().upper()
        while team_name not in [t.name for t in self.teams]:
            print(f"{Fore.RED}Invalid franchise. Choose from {', '.join(t.name for t in self.teams)}.{Style.RESET_ALL}")
            team_name = input("Choose your franchise: ").strip().upper()
        self.user_team = next(t for t in self.teams if t.name == team_name)

        # Retention mode
        while True:
            retention_mode = input("Retention mode: [A]ny number of players / [E]xact number of players: ").lower()
            if retention_mode in ['a', 'e']:
                break
            print(f"{Fore.RED}Enter 'A' or 'E'.{Style.RESET_ALL}")

        if retention_mode == 'e':
            while True:
                try:
                    num_retain = int(input(f"How many players should all teams retain (1-11)? "))
                    if 1 <= num_retain <= 11:
                        break
                    print(f"{Fore.RED}Enter a number between 1 and 11.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED}Enter a valid number.{Style.RESET_ALL}")
            self.retain_players(team_name, num_retain, is_user=True)
            for team in self.teams:
                if team.name != team_name:
                    self.retain_players(team.name, num_retain, is_user=False)
        else:
            while True:
                try:
                    num_retain = int(input(f"How many players to retain for {team_name} (1-11)? "))
                    if 1 <= num_retain <= 11:
                        break
                    print(f"{Fore.RED}Enter a number between 1 and 11.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED}Enter a valid number.{Style.RESET_ALL}")
            self.retain_players(team_name, num_retain, is_user=True)
            for team in self.teams:
                if team.name != team_name:
                    num_retain = random.randint(1, 4)
                    self.retain_players(team.name, num_retain, is_user=False)
        
        random.shuffle(self.auction_pool)
        print(f"{Fore.YELLOW}Debug: Auction pool size after retention: {len(self.auction_pool)} players{Style.RESET_ALL}")
        autosimulate_all = input("Autosimulate entire auction? [y/N]: ").lower() == 'y'
        if autosimulate_all:
            speed = input("Select speed: [F]ast / [M]edium: ").lower()
            while speed not in ['f', 'm']:
                print(f"{Fore.RED}Enter 'F' or 'M'.{Style.RESET_ALL}")
                speed = input("Select speed: [F]ast / [M]edium: ").lower()
            self.autosim_speed = 'fast' if speed == 'f' else 'medium'
        else:
            self.autosim_speed = None

        print(f"\n🎯 Managing {self.user_team.name}. Budget: ₹{self.user_team.budget}L\n")

        while self.current_index < len(self.auction_pool) and not self.all_teams_full():
            self.show_dashboard()
            player = self.auction_pool[self.current_index]
            self.show_player(player)

            if autosimulate_all:
                self.simulate_bidding(player, user_participates=True, autosimulate=True)
                self.show_team_budgets()
                self.current_index += 1
                if self.current_index < len(self.auction_pool) and not self.all_teams_full() and self.autosim_speed == 'medium':
                    user_input = input("\nPress Enter to continue or 'f' for fast mode: ").lower()
                    if user_input == 'f':
                        self.autosim_speed = 'fast'
            else:
                action = input("\nWhat to do? [B]id / [O]bserve / [S]kip / [A]utosimulate / [Q]uit: ").lower()
                if action == "b":
                    if len(self.user_team.squad) >= self.user_team.max_squad_size:
                        print(f"{Fore.RED}Squad full ({self.user_team.max_squad_size} players).{Style.RESET_ALL}")
                    else:
                        self.simulate_bidding(player, user_participates=True, action=action)
                        self.show_team_budgets()
                        self.current_index += 1
                elif action == "o":
                    self.simulate_bidding(player, user_participates=False, action=action)
                    self.show_team_budgets()
                    self.current_index += 1
                elif action == "s":
                    print(f"{Fore.YELLOW}Skipping {player['name']}, but ensuring sale.{Style.RESET_ALL}")
                    self.simulate_bidding(player, user_participates=False, action=action)
                    self.show_team_budgets()
                    self.current_index += 1
                elif action == "a":
                    remaining_players = len(self.auction_pool) - self.current_index
                    while True:
                        try:
                            num_players = int(input(f"How many players to autosimulate (1-{remaining_players})? "))
                            if 1 <= num_players <= remaining_players:
                                break
                            print(f"{Fore.RED}Enter a number between 1 and {remaining_players}.{Style.RESET_ALL}")
                        except ValueError:
                            print(f"{Fore.RED}Enter a valid number.{Style.RESET_ALL}")
                    for _ in range(num_players):
                        if self.current_index >= len(self.auction_pool) or self.all_teams_full():
                            break
                        player = self.auction_pool[self.current_index]
                        self.show_dashboard()
                        self.show_player(player)
                        self.simulate_bidding(player, user_participates=True, autosimulate=True, action=action)
                        self.show_team_budgets()
                        self.current_index += 1
                elif action == "q":
                    break
                else:
                    print(f"{Fore.RED}Invalid input. Processing player.{Style.RESET_ALL}")
                    self.simulate_bidding(player, user_participates=False, action=action)
                    self.show_team_budgets()
                    self.current_index += 1

        print(f"\n{Fore.CYAN}🎉 Auction Concluded!{Style.RESET_ALL}")
        print(f"Final Squad ({self.user_team.name}):")
        for p in self.user_team.squad:
            print(f"{p['name']} - ₹{p['Price']}L - {p['role']}")
        print(f"Remaining Budget: ₹{self.user_team.budget}L")
        self.auction_summary()
        
        if input("\nSave final rosters to teams.json? [y/N]: ").lower() == 'y':
            self.save_teams()
        input("\nPress Enter to continue or Ctrl+C to exit...")

if __name__ == "__main__":
    auction = Auction()
    auction.run()