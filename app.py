from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import game_logic
import traceback
import random
# import datetime # For timestamps - No longer needed here, AuctionManager handles its own timestamps

app = Flask(__name__)
app.secret_key = os.urandom(24)

TEAMS_DISPLAY_DATA = {
    "CSK": {"id": "csk", "logo": "CSK.png", "color": "#F9CD05", "secondary_color": "#1D418C", "name": "Chennai Super Kings"},
    "MI":  {"id": "mi", "logo": "MI.png", "color": "#005FA2", "secondary_color": "#FFCC32", "name": "Mumbai Indians"},
    "KKR": {"id": "kkr", "logo": "KKR.png", "color": "#3F2A56", "secondary_color": "#D4AF37", "name": "Kolkata Knight Riders"},
    "RCB": {"id": "rcb", "logo": "rcb.png", "color": "#A31D21", "secondary_color": "#000000", "name": "Royal Challengers Bengaluru"},
    "DC":  {"id": "dc", "logo": "DC.png", "color": "#2561AE", "secondary_color": "#D71921", "name": "Delhi Capitals"},
    "RR":  {"id": "rr", "logo": "RR---New-Logo.png", "color": "#004BA0", "secondary_color": "#D4AF37", "name": "Rajasthan Royals"},
    "SRH": {"id": "srh", "logo": "SRH.png", "color": "#F27024", "secondary_color": "#1B1920", "name": "Sunrisers Hyderabad"},
    "PBKS": {"id": "pbks", "logo": "PBKS.png", "color": "#DD1F2D", "secondary_color": "#FFFFFF", "name": "Punjab Kings"}
}

# --- AuctionManager Helper Functions ---
def _get_auction_manager_instance_from_session():
    """
    Initializes or rehydrates an AuctionManager instance using data from the session.
    It ensures that the Team objects within the AuctionManager are consistent
    with the latest state stored in session['teams_current_state'].
    """
    initial_pool = session.get('initial_auction_pool')
    initial_teams_json = session.get('initial_teams_json_data')
    teams_current_state = session.get('teams_current_state') # This is dict form of teams
    auction_manager_session_state = session.get('auction_manager_state')

    if not initial_pool or not initial_teams_json or not teams_current_state:
        # This indicates a problem, possibly session cleared or first time error
        # print("Error: Missing critical data in session for AuctionManager rehydration.")
        return None # Or raise an exception

    # 1. Create a base AuctionManager instance (this also creates its internal Team objects)
    auction_manager = game_logic.AuctionManager(initial_pool, initial_teams_json)

    # 2. Synchronize AuctionManager's internal Team objects with teams_current_state from session
    #    This is similar to part of setup_auction_stage, ensuring budgets and squads are current.
    for team_id_key, team_data_from_session in teams_current_state.items():
        team_obj_in_manager = auction_manager.teams.get(team_id_key.upper())
        if team_obj_in_manager:
            team_obj_in_manager.budget = team_data_from_session.get('budget', team_obj_in_manager.budget)

            # Reconstruct squad for the Team object based on names and prices in session state
            rehydrated_squad = []
            player_names_in_session_squad = team_data_from_session.get('squad_after_retention', [])
            player_prices_in_session = team_data_from_session.get('player_prices', {})

            for p_name in player_names_in_session_squad:
                p_detail = next((p.copy() for p in initial_pool if p['name'] == p_name), None)
                if p_detail:
                    price = player_prices_in_session.get(p_name, 0) # Default price to 0 if not found
                    p_detail['Price'] = price
                    rehydrated_squad.append(p_detail)
            team_obj_in_manager.squad = rehydrated_squad
        else:
            # print(f"Warning: Team {team_id_key} from teams_current_state not found in AuctionManager internal teams during rehydration.")
            pass


    # 3. Apply saved AuctionManager state (if it exists)
    if auction_manager_session_state:
        auction_manager.current_auction_pool_for_bidding = auction_manager_session_state.get('current_auction_pool_for_bidding', [])
        auction_manager.sold_players_log = auction_manager_session_state.get('sold_players_log', [])
        auction_manager.unsold_players_log = auction_manager_session_state.get('unsold_players_log', [])
        auction_manager.current_player_auction_index = auction_manager_session_state.get('current_player_auction_index', -1)
        auction_manager.current_player_up_for_auction = auction_manager_session_state.get('current_player_up_for_auction', None)
        auction_manager.current_bids_log_for_player = auction_manager_session_state.get('current_bids_log_for_player', [])
        auction_manager.current_highest_bid_amount = auction_manager_session_state.get('current_highest_bid_amount', 0)

        highest_bidder_team_name = auction_manager_session_state.get('current_highest_bidder_team_name')
        if highest_bidder_team_name:
            auction_manager.current_highest_bidder_team_obj = auction_manager.get_team_object_by_name(highest_bidder_team_name)
        else:
            auction_manager.current_highest_bidder_team_obj = None
        # auction_over_flag is derived by is_auction_over() method or start_bidding_for_next_player result

    return auction_manager

def _save_auction_state_to_session(auction_manager):
    """
    Saves the operational state of the AuctionManager and the state of its Team objects
    back into the Flask session.
    """
    if not auction_manager:
        # print("Error: No AuctionManager instance provided to save_auction_state.")
        return

    # 1. Extract serializable state from AuctionManager
    auction_manager_serializable_state = {
        'current_auction_pool_for_bidding': auction_manager.current_auction_pool_for_bidding,
        'sold_players_log': auction_manager.sold_players_log,
        'unsold_players_log': auction_manager.unsold_players_log,
        'current_player_auction_index': auction_manager.current_player_auction_index,
        'current_player_up_for_auction': auction_manager.current_player_up_for_auction, # Assumed to be a dict
        'current_bids_log_for_player': auction_manager.current_bids_log_for_player, # Assumed to be list of dicts
        'current_highest_bid_amount': auction_manager.current_highest_bid_amount,
        'current_highest_bidder_team_name': auction_manager.current_highest_bidder_team_obj.name if auction_manager.current_highest_bidder_team_obj else None,
        # auction_over_flag is not explicitly stored here, derived by logic in auction_main
    }
    session['auction_manager_state'] = auction_manager_serializable_state

    # 2. Update session['teams_current_state'] from AuctionManager's internal Team objects
    # This is crucial because AuctionManager's Team objects are modified during auction (e.g. budget, squad)
    teams_current_state_updated = session.get('teams_current_state', {})
    for team_id_key, team_obj_in_manager in auction_manager.teams.items():
        if team_id_key.lower() in teams_current_state_updated: # Ensure case consistency, session uses lowercase id
            teams_current_state_updated[team_id_key.lower()]['budget'] = team_obj_in_manager.budget
            teams_current_state_updated[team_id_key.lower()]['squad_after_retention'] = [p['name'] for p in team_obj_in_manager.squad]

            # Update player_prices within teams_current_state
            current_prices = teams_current_state_updated[team_id_key.lower()].get('player_prices', {})
            for player_in_squad in team_obj_in_manager.squad:
                current_prices[player_in_squad['name']] = player_in_squad.get('Price', 0) # Price is set in Team.add_player_to_squad
            teams_current_state_updated[team_id_key.lower()]['player_prices'] = current_prices
        else:
            # print(f"Warning: Team {team_id_key} from AuctionManager not found in session's teams_current_state during save.")
            pass

    session['teams_current_state'] = teams_current_state_updated
    session.modified = True # Ensure session changes are saved

# --- End AuctionManager Helper Functions ---


@app.route('/')
def index():
    session.clear()
    return render_template('select_team.html', teams_display_data=TEAMS_DISPLAY_DATA)

@app.route('/select_team_action', methods=['POST'])
def select_team_action():
    selected_team_display_key = request.form.get('selected_team_key')
    if not selected_team_display_key or selected_team_display_key not in TEAMS_DISPLAY_DATA:
        return redirect(url_for('index'))

    user_team_id_json = TEAMS_DISPLAY_DATA[selected_team_display_key]["id"]
    session['user_team_id'] = user_team_id_json
    session['user_team_display_info'] = TEAMS_DISPLAY_DATA[selected_team_display_key]

    try:
        initial_pool, initial_teams_json_data = game_logic.initialize_auction_data()
        session['initial_auction_pool'] = initial_pool
        session['initial_teams_json_data'] = initial_teams_json_data

        all_teams_objects = {}
        for team_id_key, team_player_names in initial_teams_json_data.items():
            all_teams_objects[team_id_key] = game_logic.Team(
                name=team_id_key,
                players_json_list=team_player_names,
                full_auction_pool=initial_pool
            )

        teams_runtime_state = {}
        for team_id, team_obj in all_teams_objects.items():
            teams_runtime_state[team_id] = {
                "name": team_obj.name, "budget": team_obj.budget,
                "squad_before_retention": [p["name"] for p in team_obj.squad],
                "squad_after_retention": [],
                "player_prices": {}, # To store price for each player in squad_after_retention
                "max_squad_size": team_obj.max_squad_size, "min_batters": team_obj.min_batters,
                "min_bowlers": team_obj.min_bowlers, "min_wicketkeepers": team_obj.min_wicketkeepers,
                "min_allrounders": team_obj.min_allrounders
            }
        session['teams_current_state'] = teams_runtime_state
        session['auction_pool_available_for_auction'] = [p.copy() for p in initial_pool]
        session['sold_players_history'] = [] # Initialize history of sold players

    except Exception as e:
        detailed_error = traceback.format_exc()
        # print(f"Error initializing game data: {e}\n{detailed_error}")
        return f"Error during game data initialization: {str(e)}. Check server logs. <a href='{url_for('index')}'>Back</a>"

    return redirect(url_for('retention_home'))

@app.route('/retention')
def retention_home():
    user_team_id = session.get('user_team_id')
    if not user_team_id: return redirect(url_for('index'))

    user_team_display_info = session.get('user_team_display_info', {})
    teams_state_all = session.get('teams_current_state', {})
    user_team_current_state = teams_state_all.get(user_team_id)

    if not user_team_current_state:
         return f"User team state for {user_team_id} not found. <a href='{url_for('index')}'>Back</a>"

    initial_auction_pool = session.get('initial_auction_pool', [])
    user_squad_player_names_before_ret = user_team_current_state.get('squad_before_retention', [])
    user_squad_details_before_ret = [p for name in user_squad_player_names_before_ret
                                     for p in initial_auction_pool if p['name'] == name]
    user_squad_details_before_ret.sort(key=lambda p: p.get('demand', 0), reverse=True)

    return render_template('retention_form.html',
                           user_team_display_name=user_team_display_info.get('name'),
                           user_team_id=user_team_id,
                           user_team_initial_squad_details=user_squad_details_before_ret,
                           user_team_budget=user_team_current_state.get('budget'))

@app.route('/retention/process', methods=['POST'])
def process_retention_choices():
    user_team_id = session.get('user_team_id')
    if not user_team_id: return redirect(url_for('index'))

    retention_mode = request.form.get('retention_mode')
    retained_player_names = request.form.getlist('retained_players')
    max_exact_retention_limit = 5

    if retention_mode == 'exact':
        try:
            num_retain_exact_all_teams = int(request.form.get('num_retain_exact', 0))
            if not (1 <= num_retain_exact_all_teams <= max_exact_retention_limit):
                 raise ValueError(f"Exact retention number must be between 1 and {max_exact_retention_limit}.")
        except ValueError as ve:
            return f"Error: {str(ve)} <a href='{url_for('retention_home')}'>Try Again</a>"
    else: # any_number mode
        num_retain_exact_all_teams = 0 # Not used, but ensures it's defined

    teams_state_all = session.get('teams_current_state', {}).copy()
    auction_pool_after_retention = [p.copy() for p in session.get('initial_auction_pool', [])]
    clean_initial_pool_for_sourcing = [p.copy() for p in session.get('initial_auction_pool', [])]

    user_team_obj = game_logic.Team(name=user_team_id, initial_budget=teams_state_all[user_team_id]['budget'])
    user_initial_squad_names = teams_state_all[user_team_id]['squad_before_retention']
    user_team_obj.squad = [p for name in user_initial_squad_names for p in clean_initial_pool_for_sourcing if p['name'] == name]

    num_to_retain_for_user = len(retained_player_names) if retention_mode == 'any_number' else num_retain_exact_all_teams
    if retention_mode == 'exact' and len(retained_player_names) != num_to_retain_for_user:
        return f"Select exactly {num_to_retain_for_user} players for 'Exact Number' mode. <a href='{url_for('retention_home')}'>Try Again</a>"
    if retention_mode == 'any_number' and not (0 <= num_to_retain_for_user <= 8):
         return f"Select 0-8 players for 'Any Number' mode. <a href='{url_for('retention_home')}'>Try Again</a>"

    try:
        user_team_obj, auction_pool_after_retention = game_logic.perform_retention_for_team(
            user_team_obj, auction_pool_after_retention, num_to_retain_for_user, retained_player_names, True)
    except Exception as e:
        return f"Error during user retention: {str(e)} <a href='{url_for('retention_home')}'>Try Again</a>"

    teams_state_all[user_team_id]['budget'] = user_team_obj.budget
    teams_state_all[user_team_id]['squad_after_retention'] = [p['name'] for p in user_team_obj.squad]
    teams_state_all[user_team_id]['player_prices'] = {p['name']: p['Price'] for p in user_team_obj.squad}


    for team_id_iter, team_data_iter in teams_state_all.items():
        if team_id_iter == user_team_id: continue
        ai_team_obj = game_logic.Team(name=team_id_iter, initial_budget=team_data_iter['budget'])
        ai_initial_squad_names = team_data_iter['squad_before_retention']
        ai_team_obj.squad = [p for name in ai_initial_squad_names for p in clean_initial_pool_for_sourcing if p['name'] == name]

        num_to_retain_for_ai = num_retain_exact_all_teams if retention_mode == 'exact' else random.randint(1, min(4, len(ai_team_obj.squad) if ai_team_obj.squad else 1))
        num_to_retain_for_ai = min(num_to_retain_for_ai, ai_team_obj.max_squad_size -1, len(ai_team_obj.squad))
        if num_to_retain_for_ai < 0: num_to_retain_for_ai = 0

        try:
            ai_team_obj, auction_pool_after_retention = game_logic.perform_retention_for_team(
                ai_team_obj, auction_pool_after_retention, num_to_retain_for_ai, None, False)
        except Exception as e:
             return f"Error in AI team ({team_id_iter}) retention: {str(e)} <a href='{url_for('retention_home')}'>Try Again</a>"

        teams_state_all[team_id_iter]['budget'] = ai_team_obj.budget
        teams_state_all[team_id_iter]['squad_after_retention'] = [p['name'] for p in ai_team_obj.squad]
        teams_state_all[team_id_iter]['player_prices'] = {p['name']: p['Price'] for p in ai_team_obj.squad}

    session['teams_current_state'] = teams_state_all
    session['auction_pool_available_for_auction'] = auction_pool_after_retention
    session['auction_runtime_state'] = {'current_player_index': -1} # Initialize for auction page

    return redirect(url_for('retention_summary'))

@app.route('/retention_summary')
def retention_summary():
    user_team_id = session.get('user_team_id')
    user_team_display_info = session.get('user_team_display_info')
    teams_current_state = session.get('teams_current_state')
    initial_auction_pool = session.get('initial_auction_pool')

    if not all([user_team_id, user_team_display_info, teams_current_state, initial_auction_pool]):
        # Redirect to home or an error page if essential data is missing
        return redirect(url_for('index'))

    # Convert player names in squad_after_retention to full player objects for the template
    # The template expects player objects with 'id', 'name', 'role'
    # teams_current_state has squad_after_retention as list of names.
    # initial_auction_pool has full player details but uses 'name' not 'id' for matching in this context.

    processed_teams_current_state = {}
    for team_id, team_data in teams_current_state.items():
        processed_team_data = team_data.copy()
        retained_player_details_list = []
        for player_name in team_data.get('squad_after_retention', []):
            player_obj = get_player_details_from_pool(player_name, initial_auction_pool)
            if player_obj:
                 # The template uses 'id' from the player object, ensure it's there.
                 # The price is fixed at 150L for retained players as per requirement.
                retained_player_details_list.append(player_obj)
        processed_team_data['players_details'] = retained_player_details_list # Use this new key in template
        processed_teams_current_state[team_id] = processed_team_data

    # The user_team_display_info already has an 'id' field ('csk', 'mi' etc)
    # The template also expects this 'id' to correctly identify the user's team within processed_teams_current_state

    return render_template('retention_summary.html',
                           user_team_display_info=user_team_display_info, # Contains user team 'id' and 'name'
                           teams_current_state=processed_teams_current_state, # Contains all teams, with 'players_details'
                           initial_auction_pool=initial_auction_pool) # For player lookups if any (though ideally pre-processed)


def get_player_details_from_pool(player_name, auction_pool_list):
    return next((p for p in auction_pool_list if p['name'] == player_name), None)

# initialize_auction_turn_state_for_new_player function is removed as AuctionManager.start_bidding_for_next_player
# now handles the initialization of bid logs including the initial system message with timestamp.

@app.route('/auction')
def auction_main():
    user_team_id = session.get('user_team_id')
    if not user_team_id: return redirect(url_for('index'))

    # Initialize AuctionManager on first visit after retention or if session is new
    if 'auction_manager_state' not in session:
        initial_pool = session.get('initial_auction_pool')
        initial_teams_json = session.get('initial_teams_json_data')
        teams_state_after_retention = session.get('teams_current_state')
        auction_pool_after_retention = session.get('auction_pool_available_for_auction')

        if not all([initial_pool, initial_teams_json, teams_state_after_retention, auction_pool_after_retention]):
            # print("Error: Missing data for initial AuctionManager setup.")
            return redirect(url_for('index')) # Or an error page

        auction_manager = game_logic.AuctionManager(initial_pool, initial_teams_json)
        auction_manager.setup_auction_stage(teams_state_after_retention, auction_pool_after_retention)
        # Initial save to populate session['auction_manager_state'] and sync teams_current_state
        _save_auction_state_to_session(auction_manager)

    # Get (potentially rehydrated) AuctionManager instance
    auction_manager = _get_auction_manager_instance_from_session()
    if not auction_manager:
        # print("Error: Could not get AuctionManager instance.")
        return redirect(url_for('index')) # Or an error page

    # Check if auction is over
    if auction_manager.is_auction_over():
        # Ensure any final state is saved before redirecting
        _save_auction_state_to_session(auction_manager)
        return redirect(url_for('auction_summary_page'))

    # If no player is up for auction (and auction not over), start bidding for the next one
    if auction_manager.current_player_up_for_auction is None:
        _player_obj, _highest_bid, auction_just_ended = auction_manager.start_bidding_for_next_player()
        _save_auction_state_to_session(auction_manager) # Save state after fetching next player
        if auction_just_ended:
            return redirect(url_for('auction_summary_page'))
        # If a new player was fetched, auction_manager instance is updated, re-fetch for local vars if needed for immediate use
        # Though for rendering, the updated auction_manager from _get_auction_manager_instance_from_session on next request, or direct use, is fine.
        # No, we need to use the current auction_manager instance that was just updated.

    # Ensure we have the latest teams_current_state for display (user team budget etc.)
    # _get_auction_manager_instance_from_session would have synced AM.teams based on session's teams_current_state
    # But if AM operations modified teams (not in this GET route, but good practice), then _save_auction_state_to_session
    # would have updated session's teams_current_state. For display, we read fresh from session.
    teams_all_current_state_display = session.get('teams_current_state', {})
    user_team_current_data_display = teams_all_current_state_display.get(user_team_id, {})


    current_highest_bidder_name_display = "None"
    if auction_manager.current_highest_bidder_team_obj:
        bidder_display_key = auction_manager.current_highest_bidder_team_obj.name.upper() # e.g. "CSK"
        bidder_display_info = TEAMS_DISPLAY_DATA.get(bidder_display_key)
        current_highest_bidder_name_display = bidder_display_info['name'] if bidder_display_info else bidder_display_key


    all_teams_budgets_display_info = [{
        "name": TEAMS_DISPLAY_DATA.get(team_id_key.upper(), {}).get('name', team_id_key.upper()),
        "budget": team_data_val.get('budget'),
        "squad_count": len(team_data_val.get('squad_after_retention', []))
    } for team_id_key, team_data_val in teams_all_current_state_display.items()]

    user_squad_names_display = user_team_current_data_display.get('squad_after_retention', [])
    initial_pool_for_details_display = session.get('initial_auction_pool', []) # For roles, base stats etc.
    player_prices_for_user_team_display = user_team_current_data_display.get('player_prices', {})
    user_squad_full_details_display = []
    for name in user_squad_names_display:
        player_obj_detail = get_player_details_from_pool(name, initial_pool_for_details_display)
        if player_obj_detail:
             price = player_prices_for_user_team_display.get(name, "Retained")
             display_price_str = f"₹{price}L" if isinstance(price, (int, float)) else price
             user_squad_full_details_display.append({**player_obj_detail, "display_price": display_price_str})

    # Data for the template directly from auction_manager state
    # No need for the old auction_runtime_state anymore
    return render_template('auction.html',
                           user_team_display_name=TEAMS_DISPLAY_DATA.get(user_team_id.upper(),{}).get('name','Your Team'),
                           user_team_current_budget=user_team_current_data_display.get('budget'),
                           user_team_max_squad=user_team_current_data_display.get('max_squad_size', 18), # This might be from rules or team obj
                           user_squad_display=user_squad_full_details_display,

                           # Data from AuctionManager
                           current_player_for_auction=auction_manager.current_player_up_for_auction, # dict
                           bids_log=auction_manager.current_bids_log_for_player, # list of dicts
                           current_highest_bid=auction_manager.current_highest_bid_amount, # number
                           current_highest_bidder_display_name=current_highest_bidder_name_display, # string

                           all_teams_budgets_info=all_teams_budgets_display_info,
                           total_players_in_auction_pool=len(auction_manager.current_auction_pool_for_bidding),
                           current_player_auction_number=auction_manager.current_player_auction_index + 1,
                           auction_over=auction_manager.is_auction_over() # Pass auction over flag
                           )

@app.route('/auction/summary')
def auction_summary_page():
    teams_final_state = session.get('teams_current_state', {})

    # Get auction results from AuctionManager's state
    auction_manager_state = session.get('auction_manager_state', {})
    sold_players_log = auction_manager_state.get('sold_players_log', [])
    unsold_players_log = auction_manager_state.get('unsold_players_log', []) # Potentially display this too

    # The sold_players_log from AuctionManager already contains:
    # {"name": player_name, "price": final_price, "team_id": winning_team_obj.name, "role": player_role}
    # We can augment teams_final_state with display names if needed, but player details are mostly in sold_players_log

    for team_id, team_data in teams_final_state.items():
        team_data['player_price_details'] = []
        player_prices = team_data.get('player_prices', {}) # Contains prices for retained and bought players
        squad_player_names = team_data.get('squad_after_retention', []) # This list contains names of all players in squad

        for player_name in squad_player_names:
            price = player_prices.get(player_name, "N/A")
            price_str = f"₹{price}L" if isinstance(price, (int, float)) else str(price)

            player_role = "N/A"
            # Try to get role from sold_players_log first for auctioned players
            sold_player_entry = next((p for p in sold_players_log if p['name'] == player_name and p['team_id'].lower() == team_id.lower()), None)
            if sold_player_entry:
                player_role = sold_player_entry.get('role', 'N/A')
            else: # Player might be retained, look up in initial_pool
                initial_pool = session.get('initial_auction_pool', [])
                player_detail_from_pool = get_player_details_from_pool(player_name, initial_pool)
                if player_detail_from_pool:
                    player_role = player_detail_from_pool.get('role', 'N/A')

            team_data['player_price_details'].append({"name": player_name, "role": player_role, "price_str": price_str})

        team_data['display_name'] = TEAMS_DISPLAY_DATA.get(team_id.upper(), {}).get('name', team_id.upper())

    # Pass the consolidated sold_players_log to the template.
    # The template might need adjustment if it was relying on a different structure for sold_players_history.
    return render_template('summary.html',
                           teams_final_state_display=teams_final_state,
                           sold_players_summary_display=sold_players_log, # New name for clarity
                           unsold_players_summary_display=unsold_players_log) # Optional: for display

@app.route('/auction/bid', methods=['POST'])
def auction_bid():
    user_team_id = session.get('user_team_id')
    if not user_team_id:
        return redirect(url_for('index'))

    bid_amount_str = request.form.get('bid_amount')
    if not bid_amount_str:
        # flash("Bid amount is required.", "error") # Optional: add flash messaging
        return redirect(url_for('auction_main'))

    try:
        bid_amount = int(bid_amount_str)
    except ValueError:
        # flash("Invalid bid amount.", "error")
        return redirect(url_for('auction_main'))

    auction_manager = _get_auction_manager_instance_from_session()
    if not auction_manager or auction_manager.is_auction_over() or not auction_manager.current_player_up_for_auction:
        # flash("Auction is over or no player is currently up for bidding.", "warning")
        return redirect(url_for('auction_main'))

    user_team_obj = auction_manager.get_team_object_by_name(user_team_id)
    if not user_team_obj:
        # flash("User team data not found.", "error")
        return redirect(url_for('index'))

    bid_successful, message = auction_manager.process_user_bid(user_team_obj, bid_amount)
    # flash(message, "success" if bid_successful else "error") # Optional

    if bid_successful:
        # Trigger AI bids only if user bid was successful
        _ai_winner_obj, ai_message = auction_manager.trigger_ai_bids_after_user_action(user_team_obj.name)
        # flash(ai_message, "info") # Optional for AI bidding updates

    _save_auction_state_to_session(auction_manager)
    return redirect(url_for('auction_main'))

@app.route('/auction_finalize_player', methods=['POST'])
def auction_finalize_player():
    user_team_id = session.get('user_team_id')
    if not user_team_id:
        return redirect(url_for('index'))

    auction_manager = _get_auction_manager_instance_from_session()
    if not auction_manager or not auction_manager.current_player_up_for_auction:
        # flash("No player auction to finalize or auction manager not found.", "warning")
        # If auction is over, is_auction_over() check in auction_main will redirect to summary.
        # This route is mainly if a player is active.
        return redirect(url_for('auction_main'))

    # Finalize the current player (sell or mark as unsold)
    # This method updates team squads/budgets within AuctionManager's Team objects
    # and logs the player as sold/unsold.
    # It also sets current_player_up_for_auction to None.
    _sold, message, _winning_team_id, _auction_now_over = auction_manager.finalize_current_player_auction()
    # flash(message, "info") # Optional

    # Save changes to AuctionManager state and teams_current_state (which reflects budget/squad changes)
    _save_auction_state_to_session(auction_manager)

    # Redirecting to auction_main will then pick the next player or go to summary if auction ended
    return redirect(url_for('auction_main'))

# Old /auction/observe and /auction/skip routes are now removed as their functionality
# is covered by the new auction flow:
# - AI bids are triggered automatically after a user's valid bid.
# - Finalizing a player (which includes passing) is handled by /auction_finalize_player.

# Test initialization route (can be kept or removed)
@app.route('/test_initialization/<team_key_for_test>')
def test_initialization(team_key_for_test):
    session.clear()
    selected_team_display_key = team_key_for_test.upper()
    if not selected_team_display_key or selected_team_display_key not in TEAMS_DISPLAY_DATA:
        return jsonify({"error": "Invalid team key for test", "key_tested": team_key_for_test}), 400
    user_team_id_json = TEAMS_DISPLAY_DATA[selected_team_display_key]["id"]
    session['user_team_id'] = user_team_id_json
    try:
        initial_pool, initial_teams_json_data = game_logic.initialize_auction_data()
        all_teams_objects = {tid: game_logic.Team(name=tid, players_json_list=p_list,full_auction_pool=initial_pool)
                             for tid, p_list in initial_teams_json_data.items()}
        teams_runtime_state = {tid: {"name": to.name, "budget": to.budget,
                                   "squad_before_retention": [p["name"] for p in to.squad]}
                               for tid, to in all_teams_objects.items()}
        user_team_session_data = teams_runtime_state.get(user_team_id_json)
        return jsonify({
            "status": "success", "user_team_id": user_team_id_json,
            "initial_pool_count": len(initial_pool),
            "teams_initialized_count": len(teams_runtime_state),
            "user_team_budget": user_team_session_data.get("budget") if user_team_session_data else "Error: team not found",
            "user_team_squad_pre_ret_count": len(user_team_session_data.get("squad_before_retention",[])) if user_team_session_data else "Error"
        }), 200
    except Exception as e:
        return jsonify({"error": f"Initialization failed: {str(e)}", "details": traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
