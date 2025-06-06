import json
import random
import datetime # For timestamps

# NAME_MAPPING and other initial parts (get_role, Team, AuctionManager etc. remain unchanged from the previous version)

NAME_MAPPING = {
    "MS Dhoni": "MS Dhoni", "RD Gaikwad": "RD Gaikwad", "DP Conway": "DP Conway", "AM Rahane": "AM Rahane",
    "S Dubey": "S Dubey", "RA Jadeja": "RA Jadeja", "MM Ali": "MM Ali", "DL Chahar": "DL Chahar",
    "TU Deshpande": "TU Deshpande", "M Theekshana": "M Theekshana", "M Pathirana": "M Pathirana",
    "RG Sharma": "RG Sharma", "Ishan Kishan": "Ishan Kishan", "SA Yadav": "SA Yadav", "Tilak Varma": "Tilak Varma",
    "TH David": "TH David", "C Green": "C Green", "JC Archer": "JC Archer", "JJ Bumrah": "JJ Bumrah",
    "JP Behrendorff": "JP Behrendorff", "PP Chawla": "PP Chawla", "K Gowtham": "K Gowtham",
    "N Rana": "N Rana", "VR Iyer": "VR Iyer", "SP Narine": "SP Narine", "AD Russell": "AD Russell",
    "RK Singh": "RK Singh", "Rahmanullah Gurbaz": "Rahmanullah Gurbaz", "LH Ferguson": "LH Ferguson",
    "CV Varun": "CV Varun", "UT Yadav": "UT Yadav", "TG Southee": "TG Southee", "F du Plessis": "F du Plessis",
    "V Kohli": "V Kohli", "GJ Maxwell": "GJ Maxwell", "MK Lomror": "MK Lomror", "KD Karthik": "KD Karthik",
    "WD Parnell": "WD Parnell", "Mohammed Siraj": "Mohammed Siraj", "JR Hazlewood": "JR Hazlewood",
    "HV Patel": "HV Patel", "KV Sharma": "KV Sharma", "DA Warner": "DA Warner", "PP Shaw": "PP Shaw",
    "MR Marsh": "MR Marsh", "RR Pant": "RR Pant", "R Powell": "R Powell", "AR Patel": "AR Patel",
    "A Nortje": "A Nortje", "KK Ahmed": "KK Ahmed", "Kuldeep Yadav": "Kuldeep Yadav", "L Ngidi": "L Ngidi",
    "SV Samson": "SV Samson", "YBK Jaiswal": "YBK Jaiswal", "JC Buttler": "JC Buttler", "D Padikkal": "D Padikkal",
    "SO Hetmyer": "SO Hetmyer", "R Ashwin": "R Ashwin", "YS Chahal": "YS Chahal", "TA Boult": "TA Boult",
    "OC McCoy": "OC McCoy", "KM Asif": "KM Asif", "MA Agarwal": "MA Agarwal", "RA Tripathi": "RA Tripathi",
    "AK Markram": "AK Markram", "HC Brook": "HC Brook", "H Klaasen": "H Klaasen",
    "Washington Sundar": "Washington Sundar", "B Kumar": "B Kumar", "Umran Malik": "Umran Malik",
    "T Natarajan": "T Natarajan", "Fazalhaq Farooqi": "Fazalhaq Farooqi", "S Dhawan": "S Dhawan",
    "P Simran Singh": "P Simran Singh", "JM Bairstow": "JM Bairstow", "LS Livingstone": "LS Livingstone",
    "SM Curran": "SM Curran", "JM Sharma": "JM Sharma", "RD Chahar": "RD Chahar", "K Rabada": "K Rabada",
    "Arshdeep Singh": "Arshdeep Singh", "NT Ellis": "NT Ellis", "WP Saha": "WP Saha", "Shubman Gill": "Shubman Gill",
    "B Sai Sudharsan": "B Sai Sudharsan", "HH Pandya": "HH Pandya", "DA Miller": "DA Miller",
    "R Tewatia": "R Tewatia", "Rashid Khan": "Rashid Khan", "Mohammed Shami": "Mohammed Shami",
    "Noor Ahmad": "Noor Ahmad", "MM Sharma": "MM Sharma", "KL Rahul": "KL Rahul", "Q de Kock": "Q de Kock",
    "KH Pandya": "KH Pandya", "MP Stoinis": "MP Stoinis", "N Pooran": "N Pooran", "A Badoni": "A Badoni",
    "Ravi Bishnoi": "Ravi Bishnoi", "Mark Wood": "Mark Wood", "Avesh Khan": "Avesh Khan", "Mohsin Khan": "Mohsin Khan",
    # Added entries that might have been missing or for broader matching
    "DJ Hooda": "DJ Hooda", "KA Pollard": "KA Pollard", "SK Raina": "SK Raina", "SS Iyer": "SS Iyer",
    "KS Williamson": "KS Williamson", "MK Pandey": "MK Pandey", "AB de Villiers": "AB de Villiers",
    "EJG Morgan": "EJG Morgan", "Abdul Samad": "Abdul Samad", "M Shahrukh Khan": "M Shahrukh Khan",
    "Lalit Yadav": "Lalit Yadav", "Shahbaz Ahmed": "Shahbaz Ahmed", "R Parag": "R Parag", "KM Jadhav": "KM Jadhav",
    "SN Thakur": "SN Thakur", "M Prasidh Krishna": "M Prasidh Krishna", "Sandeep Sharma": "Sandeep Sharma",
    "DJ Bravo": "DJ Bravo", "CH Morris": "CH Morris", "Mustafizur Rahman": "Mustafizur Rahman",
    "Shivam Mavi": "Shivam Mavi", "RP Meredith": "RP Meredith", "JO Holder": "JO Holder", "DT Christian": "DT Christian",
    "NA Saini": "NA Saini", "C Sakariya": "C Sakariya", "AF Milne": "AF Milne", "Kartik Tyagi": "Kartik Tyagi",
    "Harpreet Brar": "Harpreet Brar"
}

def load_stats_from_json(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            raise ValueError(f"Error: {filepath} is not a list of dictionaries.")
        return data
    except FileNotFoundError:
        # print(f"Error: File not found {filepath}") # Optional: log this
        raise FileNotFoundError(f"Error: File not found {filepath}")
    except json.JSONDecodeError:
        # print(f"Error: Could not decode JSON from {filepath}") # Optional: log this
        raise json.JSONDecodeError(f"Error: Could not decode JSON from {filepath}", doc=filepath, pos=0)
    except Exception as e:
        # print(f"Error loading {filepath}: {e}") # Optional: log this
        raise Exception(f"Error loading {filepath}: {e}")


def load_teams_data_from_json(filepath="teams.json"):
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            teams = json.load(file)
        return teams
    except Exception as e:
        # print(f"Error loading {filepath}: {e}") # Optional: log this
        raise Exception(f"Error loading {filepath}: {e}") # Or return {} if preferred for graceful degradation

def get_role(runs, wickets, player_name):
    wicketkeepers = ['RR Pant', 'Q de Kock', 'SV Samson', 'Ishan Kishan', 'WP Saha', 'MS Dhoni', 'D Padikkal', 'P Simran Singh', 'JM Bairstow', 'KD Karthik', 'Rahmanullah Gurbaz', 'N Pooran', 'H Klaasen', 'JM Sharma']
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

INITIAL_AUCTION_POOL = []
INITIAL_TEAMS_JSON = {}

def initialize_auction_data():
    global INITIAL_AUCTION_POOL, INITIAL_TEAMS_JSON

    bat_stats_list = load_stats_from_json("batStats.json")
    bowl_stats_list = load_stats_from_json("bowlStats.json")
    INITIAL_TEAMS_JSON = load_teams_data_from_json("teams.json")

    if not INITIAL_TEAMS_JSON: # bat/bowl lists being empty is handled later by player not found
         raise Exception("Failed to load teams.json. This file is critical.")

    bowl_stats_dict = {player_stat['Player'].strip(): player_stat for player_stat in bowl_stats_list}
    merged_player_data = []
    processed_bat_players = set()

    def to_numeric(value, default_val=0, type_func=float):
        if value is None or str(value).lower() == "na" or str(value).strip() == "" or str(value).lower() == 'null':
            return default_val
        try:
            return type_func(value)
        except (ValueError, TypeError):
            return default_val

    for bat_player in bat_stats_list:
        player_name = bat_player['Player'].strip()
        processed_bat_players.add(player_name)
        bowl_player_stats = bowl_stats_dict.get(player_name, {})

        player_merged = {
            "Player": player_name,
            "Runs": to_numeric(bat_player.get("Runs"), 0, int),
            "Average": to_numeric(bat_player.get("Average"), 0.0, float),
            "SR": to_numeric(bat_player.get("SR"), 0.0, float),
            "Wickets": to_numeric(bowl_player_stats.get("Wickets"), 0, int),
            "Economy": to_numeric(bowl_player_stats.get("Economy"), 15.0, float) # Default high economy for non-bowlers
        }
        merged_player_data.append(player_merged)

    for bowl_player_name_key, bowl_player_val in bowl_stats_dict.items():
        if bowl_player_name_key not in processed_bat_players:
            player_name = bowl_player_name_key.strip()
            player_merged = {
                "Player": player_name, "Runs": 0, "Average": 0.0, "SR": 0.0,
                "Wickets": to_numeric(bowl_player_val.get("Wickets"), 0, int),
                "Economy": to_numeric(bowl_player_val.get("Economy"), 15.0, float)
            }
            merged_player_data.append(player_merged)

    current_auction_pool = []
    player_names_in_pool = set()
    for _team_name, players_in_team_from_json in INITIAL_TEAMS_JSON.items():
        for player_name_from_json_raw in players_in_team_from_json:
            player_name_from_json = str(player_name_from_json_raw).strip()
            if not player_name_from_json or player_name_from_json in player_names_in_pool:
                continue
            player_names_in_pool.add(player_name_from_json)

            stats_name_to_find = NAME_MAPPING.get(player_name_from_json, player_name_from_json)
            player_stats_found = next((p_stat for p_stat in merged_player_data if p_stat["Player"] == stats_name_to_find), None)

            if not player_stats_found:
                # If player from teams.json not in stats, create a default entry
                runs, wickets, avg_val, eco_val, sr_val = 0, 0, 0.0, 15.0, 0.0
                # print(f"Warning: Stats not found for player {player_name_from_json} (mapped to {stats_name_to_find}). Using default zero stats.")
            else:
                runs = player_stats_found.get("Runs", 0)
                wickets = player_stats_found.get("Wickets", 0)
                avg_val = player_stats_found.get("Average", 0.0)
                eco_val = player_stats_found.get("Economy", 15.0) # Use 15.0 if Economy is 0 or missing (typical for non-bowlers)
                sr_val = player_stats_found.get("SR", 0.0)
                if eco_val == 0.0 and wickets == 0 : eco_val = 15.0 # If player has no wickets, high economy

            demand = (runs / 10 + wickets * 15 + sr_val / 5) if sr_val > 0 else (runs / 10 + wickets * 15) # Adjusted wickets impact
            base_price = max(20, min(200, int(demand / 3.5))) # Adjusted divisor

            player_dict = {
                "name": player_name_from_json, "stats_name": stats_name_to_find,
                "runs": runs, "wickets": wickets,
                "avg": avg_val if avg_val != 0.0 else "NA",
                "eco": eco_val if eco_val != 15.0 else "NA", # If it's the default high, show NA
                "sr": sr_val if sr_val != 0.0 else "NA",
                "base_price": base_price, "demand": int(demand),
                "role": get_role(runs, wickets, player_name_from_json)
            }
            current_auction_pool.append(player_dict)

    INITIAL_AUCTION_POOL = current_auction_pool
    return INITIAL_AUCTION_POOL, INITIAL_TEAMS_JSON

class Team:
    def __init__(self, name, initial_budget=200000, players_json_list=None, full_auction_pool=None):
        self.name = name.upper()
        self.squad = []
        self.budget = initial_budget
        self.max_squad_size = 18
        self.min_batters = 5
        self.min_bowlers = 5
        self.min_wicketkeepers = 1
        self.min_allrounders = 2
        self.max_overseas = 6 # This is not currently enforced in logic, but good to have
        if players_json_list and full_auction_pool:
            for player_name_from_json in players_json_list:
                player_obj_from_pool = next((p.copy() for p in full_auction_pool if p["name"] == player_name_from_json), None)
                if player_obj_from_pool:
                    self.squad.append(player_obj_from_pool)

    def count_players_by_role(self, role_category):
        count = 0
        if role_category == "Batter": count = sum(1 for p in self.squad if "Batter" in p["role"] and "Wicketkeeper" not in p["role"])
        elif role_category == "Bowler": count = sum(1 for p in self.squad if p["role"] == "Bowler")
        elif role_category == "Wicketkeeper": count = sum(1 for p in self.squad if "Wicketkeeper" in p["role"])
        elif role_category == "All-Rounder": count = sum(1 for p in self.squad if p["role"] == "All-Rounder")
        return count

    def can_add_player(self, player_obj_to_add, bid_price):
        if len(self.squad) >= self.max_squad_size: return False, "Squad full"
        if self.budget < bid_price: return False, "Cannot afford"
        return True, "Can add"

    def needs_role_urgency(self, role_to_check):
        batters = self.count_players_by_role("Batter")
        bowlers = self.count_players_by_role("Bowler")
        wicketkeepers = self.count_players_by_role("Wicketkeeper")
        allrounders = self.count_players_by_role("All-Rounder")
        if "Batter" in role_to_check and "Wicketkeeper" not in role_to_check and batters < self.min_batters: return 3.0
        if role_to_check == "Bowler" and bowlers < self.min_bowlers: return 3.0
        if "Wicketkeeper" in role_to_check and wicketkeepers < self.min_wicketkeepers: return 3.5
        if role_to_check == "All-Rounder" and allrounders < self.min_allrounders: return 2.5
        if len(self.squad) < self.max_squad_size / 2 : return 1.5
        return 1.0

    def add_player_to_squad(self, player_obj, price):
        player_with_price = {**player_obj.copy(), "Price": price}
        self.squad.append(player_with_price)
        self.budget -= price
        return True

    def remove_player_from_squad_before_retention(self, player_name):
        original_len = len(self.squad)
        self.squad = [p for p in self.squad if p["name"] != player_name]
        return len(self.squad) < original_len

def perform_retention_for_team(team_obj, global_auction_pool_list, num_players_to_retain_target, list_of_player_names_to_retain=None, is_user_team=False):
    retained_this_round_for_team = []
    retention_fee_per_player = 150
    players_available_for_retention_in_team = [p.copy() for p in team_obj.squad] # squad is from teams.json initially
    players_available_for_retention_in_team.sort(key=lambda p: p.get("demand",0), reverse=True) # Use .get for safety

    if is_user_team and list_of_player_names_to_retain:
        for name_to_retain in list_of_player_names_to_retain:
            player_to_retain_obj = next((p for p in players_available_for_retention_in_team if p["name"] == name_to_retain), None)
            if player_to_retain_obj and len(retained_this_round_for_team) < num_players_to_retain_target:
                retained_this_round_for_team.append(player_to_retain_obj)
    else: # AI retention logic
        retained_this_round_for_team = players_available_for_retention_in_team[:num_players_to_retain_target]

    final_squad_for_team_after_this_retention = []
    for player_data_to_retain in retained_this_round_for_team:
        if team_obj.budget >= retention_fee_per_player:
            team_obj.budget -= retention_fee_per_player
            player_with_retention_price = {**player_data_to_retain, "Price": retention_fee_per_player}
            final_squad_for_team_after_this_retention.append(player_with_retention_price)
            global_auction_pool_list[:] = [p for p in global_auction_pool_list if p.get("name") != player_data_to_retain.get("name")]
        else:
            pass # Cannot afford, player stays in pool (or rather, was never removed)
    team_obj.squad = final_squad_for_team_after_this_retention # Squad now only has retained players
    return team_obj, global_auction_pool_list

def simulate_ai_bidding_for_player(player_being_auctioned, participating_ai_teams_list, current_highest_bid_amount, user_team_name_str_if_involved):
    bids_log_for_this_round = []
    new_highest_bid_this_round = current_highest_bid_amount
    winning_team_obj_this_round = None
    eligible_ai_bidders = [
        team for team in participating_ai_teams_list
        if team.name.upper() != user_team_name_str_if_involved.upper()
           and team.can_add_player(player_being_auctioned, new_highest_bid_this_round + 10)[0] # Check min increment
    ]
    if not eligible_ai_bidders:
        return new_highest_bid_this_round, winning_team_obj_this_round, bids_log_for_this_round

    eligible_ai_bidders.sort(key=lambda t: (t.needs_role_urgency(player_being_auctioned.get("role","Batter")), player_being_auctioned.get("demand",0), t.budget), reverse=True)

    if not eligible_ai_bidders: # Re-check after sort, though unlikely to change emptiness
        return new_highest_bid_this_round, winning_team_obj_this_round, bids_log_for_this_round

    top_ai_bidder_candidate = eligible_ai_bidders[0]
    role_need_multiplier = top_ai_bidder_candidate.needs_role_urgency(player_being_auctioned.get("role","Batter"))
    ai_perceived_value = player_being_auctioned.get("base_price",20) + (player_being_auctioned.get("demand",0) * role_need_multiplier * random.uniform(0.7, 1.3))
    max_bid_ai_willing_to_make = min(ai_perceived_value, top_ai_bidder_candidate.budget * random.uniform(0.3, 0.5), top_ai_bidder_candidate.budget -10) # ensure some budget left
    potential_ai_bid = int((new_highest_bid_this_round + random.choice([10, 20, 50, 70])) / 10) * 10 # round to 10s

    if potential_ai_bid <= top_ai_bidder_candidate.budget and potential_ai_bid <= max_bid_ai_willing_to_make and potential_ai_bid > new_highest_bid_this_round:
        new_highest_bid_this_round = potential_ai_bid
        winning_team_obj_this_round = top_ai_bidder_candidate
        bids_log_for_this_round.append({"team_name": top_ai_bidder_candidate.name, "bid_amount": new_highest_bid_this_round, "timestamp": "now"})

    return new_highest_bid_this_round, winning_team_obj_this_round, bids_log_for_this_round

class AuctionManager:
    def __init__(self, all_players_master_list, team_details_from_json):
        self.original_master_auction_pool = [p.copy() for p in all_players_master_list]
        self.current_auction_pool_for_bidding = []
        self.teams = {}
        self.sold_players_log = []
        self.unsold_players_log = []
        self.current_player_auction_index = -1
        self.current_player_up_for_auction = None
        self.current_bids_log_for_player = []
        self.current_highest_bid_amount = 0
        self.current_highest_bidder_team_obj = None
        for team_name_key, initial_player_names_list in team_details_from_json.items():
            team_name_upper = team_name_key.upper()
            self.teams[team_name_upper] = Team(name=team_name_upper, players_json_list=initial_player_names_list, full_auction_pool=self.original_master_auction_pool)

    def setup_auction_stage(self, teams_state_after_retention_dict, auction_pool_after_retention_list):
        # teams_state_after_retention_dict is session['teams_current_state']
        # self.teams already contains Team objects from __init__
        # Update these Team objects based on the state from session after retention
        for team_id, team_session_data in teams_state_after_retention_dict.items():
            team_obj = self.teams.get(team_id.upper()) # team_id should be like 'csk', 'mi'
            if team_obj:
                team_obj.budget = team_session_data.get('budget', team_obj.budget)

                # Reconstruct squad with full player objects for the Team instance
                # team_session_data['squad_after_retention'] is a list of player names
                # team_session_data['player_prices'] has prices for these names

                new_squad_for_team_obj = []
                initial_pool = self.original_master_auction_pool # Use the manager's initial pool for consistency

                for player_name in team_session_data.get('squad_after_retention', []):
                    player_detail = next((p.copy() for p in initial_pool if p['name'] == player_name), None)
                    if player_detail:
                        price = team_session_data.get('player_prices', {}).get(player_name, 0) # Default to 0 if price not found
                        player_with_price = {**player_detail, "Price": price}
                        new_squad_for_team_obj.append(player_with_price)
                team_obj.squad = new_squad_for_team_obj
            else:
                # This case should ideally not happen if initial_teams_json_data and teams_current_state are consistent
                print(f"Warning: Team ID {team_id} from session state not found in AuctionManager's initial teams.")

        self.current_auction_pool_for_bidding = [p.copy() for p in auction_pool_after_retention_list]
        random.shuffle(self.current_auction_pool_for_bidding)
        self.current_player_auction_index = -1
        self.sold_players_log = []
        self.unsold_players_log = []

    def get_team_object_by_name(self, team_name_str):
        return self.teams.get(team_name_str.upper())

    def start_bidding_for_next_player(self):
        self.current_player_auction_index += 1
        if self.current_player_auction_index < len(self.current_auction_pool_for_bidding):
            self.current_player_up_for_auction = self.current_auction_pool_for_bidding[self.current_player_auction_index]
            self.current_bids_log_for_player = []
            self.current_highest_bid_amount = self.current_player_up_for_auction.get("base_price", 20)
            self.current_highest_bidder_team_obj = None
            self._log_bid_event("System", f"Auction started for {self.current_player_up_for_auction.get('name','Unknown')} (Role: {self.current_player_up_for_auction.get('role','N/A')}) at base price {self.current_highest_bid_amount}L.")
            return self.current_player_up_for_auction, self.current_highest_bid_amount, self.is_auction_over() # Return auction_over flag
        else:
            self.current_player_up_for_auction = None
            self._log_bid_event("System", "All players auctioned.")
            # self.auction_over_flag = True # Set flag here
            return None, 0, self.is_auction_over() # Return auction_over flag

    def is_auction_over(self):
        return self.current_player_auction_index >= len(self.current_auction_pool_for_bidding) -1 and self.current_player_up_for_auction is None


    def _log_bid_event(self, bidder_name, message_or_amount_info):
        entry = {"bidder": bidder_name, "info": message_or_amount_info, "timestamp": datetime.datetime.now().strftime("%H:%M:%S")}
        self.current_bids_log_for_player.append(entry)

    def process_user_bid(self, user_team_obj, bid_amount_by_user):
        if not self.current_player_up_for_auction: return False, "No player is currently up for auction."
        can_bid, reason = user_team_obj.can_add_player(self.current_player_up_for_auction, bid_amount_by_user)
        if not can_bid: return False, reason
        if bid_amount_by_user <= self.current_highest_bid_amount: return False, "Your bid must be higher than the current highest bid."
        self.current_highest_bid_amount = bid_amount_by_user
        self.current_highest_bidder_team_obj = user_team_obj
        self._log_bid_event(user_team_obj.name, f"bids {bid_amount_by_user}L.")
        return True, f"Your bid of {bid_amount_by_user}L for {self.current_player_up_for_auction.get('name','Unknown')} is now the highest."

    def trigger_ai_bids_after_user_action(self, user_team_name_str_if_involved):
        if not self.current_player_up_for_auction: return None, "No player to run AI bids for."
        ai_teams_eligible_to_bid = [team for team_name, team in self.teams.items() if not self.current_highest_bidder_team_obj or team_name != self.current_highest_bidder_team_obj.name]
        new_ai_bid_amount, winning_ai_team_after_this_round, ai_bid_logs_this_round = simulate_ai_bidding_for_player(self.current_player_up_for_auction, ai_teams_eligible_to_bid, self.current_highest_bid_amount, user_team_name_str_if_involved)
        for log_entry in ai_bid_logs_this_round:
             self._log_bid_event(log_entry["team_name"], f"bids {log_entry['bid_amount']}L.")
        if winning_ai_team_after_this_round and new_ai_bid_amount > self.current_highest_bid_amount:
            self.current_highest_bid_amount = new_ai_bid_amount
            self.current_highest_bidder_team_obj = winning_ai_team_after_this_round
            return winning_ai_team_after_this_round, f"{winning_ai_team_after_this_round.name} outbids with {new_ai_bid_amount}L."
        if self.current_highest_bidder_team_obj:
             return self.current_highest_bidder_team_obj, f"{self.current_highest_bidder_team_obj.name} remains the highest bidder with {self.current_highest_bid_amount}L."
        return None, "No AI bids placed or no AI outbid the current highest."

    def finalize_current_player_auction(self):
        if not self.current_player_up_for_auction: return False, "No player auction to finalize.", None, False
        player_being_sold_or_unsold = self.current_player_up_for_auction
        final_price = self.current_highest_bid_amount
        winning_team_obj = self.current_highest_bidder_team_obj
        player_name = player_being_sold_or_unsold.get('name', 'Unknown')

        if winning_team_obj:
            # Attempt to add player to squad. This method updates budget and squad list internally.
            if winning_team_obj.add_player_to_squad(player_being_sold_or_unsold, final_price):
                self.sold_players_log.append({
                    "name": player_name,
                    "price": final_price,
                    "team_id": winning_team_obj.name,  # Store team ID
                    "role": player_being_sold_or_unsold.get("role","N/A")
                })
                self._log_bid_event("System", f"SOLD to {winning_team_obj.name} for {final_price}L.")
                # After selling, the current player is done. Set to None for next player logic.
                self.current_player_up_for_auction = None
                return True, f"{player_name} sold to {winning_team_obj.name} for {final_price}L.", winning_team_obj.name, self.is_auction_over()
            else:
                # This case implies can_add_player check failed post-bidding (e.g. budget constraint due to parallel action not modeled here)
                # Or, more likely, a logic error if can_add_player was true during bidding.
                self._log_bid_event("System", f"Sale FAILED for {player_name} to {winning_team_obj.name} (post-bid squad/budget issue). Player UNSOLD.")
                self.unsold_players_log.append(player_being_sold_or_unsold)
                self.current_player_up_for_auction = None
                return False, f"Sale failed for {player_name}. Player UNSOLD.", None, self.is_auction_over()
        else:
            # No winning bidder, player is unsold
            self._log_bid_event("System", f"{player_name} is UNSOLD at {player_being_sold_or_unsold.get('base_price',0)}L.")
            self.unsold_players_log.append(player_being_sold_or_unsold)
            self.current_player_up_for_auction = None
            return False, f"{player_name} UNSOLD.", None, self.is_auction_over()

    def get_all_teams_summary_for_display(self):
        summary_list = []
        for _team_name_key, team_obj_instance in self.teams.items(): # Use _ to indicate key is not directly used
            summary_list.append({
                "name": team_obj_instance.name, "budget_remaining": team_obj_instance.budget,
                "squad_size": len(team_obj_instance.squad),
                "players_in_squad_names": [p.get("name","N/A") for p in team_obj_instance.squad],
                "players_in_squad_full": team_obj_instance.squad
            })
        return summary_list

    def get_auction_end_summary_report(self):
        top_5_buys = sorted(self.sold_players_log, key=lambda x: x.get("price",0), reverse=True)[:5]
        team_composition_analysis = []
        for _team_name_key, team_obj_instance in self.teams.items():
            bat = team_obj_instance.count_players_by_role("Batter")
            bowl = team_obj_instance.count_players_by_role("Bowler")
            wk = team_obj_instance.count_players_by_role("Wicketkeeper")
            ar = team_obj_instance.count_players_by_role("All-Rounder")
            team_composition_analysis.append({
                "name": team_obj_instance.name, "total_players": len(team_obj_instance.squad),
                "budget_left": team_obj_instance.budget, "batters": bat, "bowlers": bowl, "wks": wk, "all_rounders": ar
            })
        return {"top_purchases": top_5_buys, "team_analysis_stats": team_composition_analysis, "sold_players": self.sold_players_log, "unsold_players": self.unsold_players_log}

# Placeholder comments for Flask interaction (already correctly formatted as comments)
# def start_new_auction_session_for_flask():
#     pass
# def process_user_retention_choices_from_flask(user_team_id, players_to_retain_names_list, num_allowed_to_retain):
#     pass
# def conduct_ai_retention_for_all_other_teams(user_team_id, pool_after_user_retention):
#     pass
# def get_next_player_for_bidding_from_flask():
#     pass
# def handle_user_bid_from_flask(user_team_id, bid_amount):
#     pass
# def handle_user_pass_or_skip_from_flask(user_team_id):
#     pass
# def get_current_auction_status_for_flask():
#     pass
