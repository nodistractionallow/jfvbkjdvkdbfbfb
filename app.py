from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import game_logic
import traceback
import random
import datetime # For timestamps

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

    return redirect(url_for('auction_main'))

def get_player_details_from_pool(player_name, auction_pool_list):
    return next((p for p in auction_pool_list if p['name'] == player_name), None)

def initialize_auction_turn_state_for_new_player(player_obj):
    return {
        "bids_log": [{"bidder": "System", "info": f"Auction for {player_obj['name']} (Base: ₹{player_obj['base_price']}L)", "timestamp": datetime.datetime.now().strftime("%H:%M:%S")}],
        "current_highest_bid": player_obj['base_price'],
        "current_highest_bidder_id": None,
        "player_sold_status_message": None
    }

@app.route('/auction')
def auction_main():
    user_team_id = session.get('user_team_id')
    if not user_team_id: return redirect(url_for('index'))

    teams_all_current_state = session.get('teams_current_state', {})
    user_team_current_data = teams_all_current_state.get(user_team_id, {})
    auction_pool = session.get('auction_pool_available_for_auction', [])
    auction_runtime_state = session.get('auction_runtime_state', {})
    current_player_index = auction_runtime_state.get('current_player_index', -1)

    current_player_object_from_session = auction_runtime_state.get('player_up_for_auction')
    is_player_active_and_unsold = current_player_object_from_session and not auction_runtime_state.get('player_sold_status_message')

    if not is_player_active_and_unsold:
        current_player_index += 1
        if current_player_index < len(auction_pool):
            next_player_obj_for_auction = auction_pool[current_player_index]
            turn_init_state = initialize_auction_turn_state_for_new_player(next_player_obj_for_auction)
            auction_runtime_state.update({
                'current_player_index': current_player_index,
                'player_up_for_auction': next_player_obj_for_auction,
                **turn_init_state
            })
            session['auction_runtime_state'] = auction_runtime_state
        else: # Auction ends
            session['auction_runtime_state']['auction_over_message'] = "All players auctioned!"
            session['auction_runtime_state'] = auction_runtime_state # Save state before redirect
            return redirect(url_for('auction_summary_page'))

    # Refresh player_to_auction after potential update
    player_to_auction = auction_runtime_state.get('player_up_for_auction')
    if not player_to_auction: # Should be caught by redirect above, but as a safeguard
         return redirect(url_for('auction_summary_page'))

    current_highest_bidder_name = "None"
    highest_bidder_id_from_session = auction_runtime_state.get('current_highest_bidder_id')
    if highest_bidder_id_from_session: # This ID is 'csk', 'mi' etc.
        # Use TEAMS_DISPLAY_DATA for full name, it expects uppercase keys like "CSK"
        bidder_display_info = TEAMS_DISPLAY_DATA.get(highest_bidder_id_from_session.upper())
        current_highest_bidder_name = bidder_display_info['name'] if bidder_display_info else highest_bidder_id_from_session.upper()

    all_teams_budgets_display = [{
        "name": TEAMS_DISPLAY_DATA.get(team_id_key.upper(), {}).get('name', team_id_key.upper()),
        "budget": team_data_val.get('budget'),
        "squad_count": len(team_data_val.get('squad_after_retention', []))
    } for team_id_key, team_data_val in teams_all_current_state.items()]

    user_squad_names = user_team_current_data.get('squad_after_retention', [])
    initial_pool_for_details = session.get('initial_auction_pool', [])
    player_prices_for_user_team = teams_all_current_state.get(user_team_id, {}).get('player_prices', {})
    user_squad_full_details = []
    for name in user_squad_names:
        player_obj_detail = get_player_details_from_pool(name, initial_pool_for_details) # Get base details
        if player_obj_detail:
             price = player_prices_for_user_team.get(name, "Retained")
             display_price_str = f"₹{price}L" if isinstance(price, (int, float)) else price
             user_squad_full_details.append({**player_obj_detail, "display_price": display_price_str})

    return render_template('auction.html',
                           user_team_display_name=TEAMS_DISPLAY_DATA.get(user_team_id.upper(),{}).get('name','Your Team'),
                           user_team_current_budget=user_team_current_data.get('budget'),
                           user_team_max_squad=user_team_current_data.get('max_squad_size', 18),
                           user_squad_display=user_squad_full_details,
                           auction_runtime_state_snapshot=auction_runtime_state,
                           current_highest_bidder_display_name=current_highest_bidder_name,
                           all_teams_budgets_info=all_teams_budgets_display,
                           total_players_in_auction_pool=len(auction_pool),
                           current_player_auction_number=auction_runtime_state.get('current_player_index', -1) + 1)

@app.route('/auction/summary')
def auction_summary_page():
    teams_final_state = session.get('teams_current_state', {})
    sold_players_history = session.get('sold_players_history', [])

    for team_id, team_data in teams_final_state.items():
        team_data['player_price_details'] = []
        player_prices = team_data.get('player_prices', {})
        for player_name in team_data.get('squad_after_retention', []):
             price = player_prices.get(player_name, "Retained") # Default if price somehow not set
             price_str = f"₹{price}L" if isinstance(price, (int, float)) else str(price)
             # Get player role from initial_auction_pool for display
             player_role = "N/A"
             initial_pool = session.get('initial_auction_pool', [])
             player_detail = get_player_details_from_pool(player_name, initial_pool)
             if player_detail: player_role = player_detail.get('role', 'N/A')
             team_data['player_price_details'].append({"name": player_name, "role": player_role, "price_str": price_str})
        # Add display name for summary page
        team_data['display_name'] = TEAMS_DISPLAY_DATA.get(team_id.upper(), {}).get('name', team_id.upper())


    return render_template('summary.html', teams_final_state_display=teams_final_state, sold_players_history_display=sold_players_history)

@app.route('/auction/bid', methods=['POST'])
def auction_bid():
    # To be fully implemented in Step 8
    return redirect(url_for('auction_main'))

@app.route('/auction/observe', methods=['POST'])
def auction_observe():
    # To be fully implemented in Step 8
    return redirect(url_for('auction_main'))

@app.route('/auction/skip', methods=['POST'])
def auction_skip():
    auction_runtime_state = session.get('auction_runtime_state', {})
    current_player_obj = auction_runtime_state.get('player_up_for_auction')
    if current_player_obj:
        # Mark player as unsold/skipped for this turn
        auction_runtime_state['player_sold_status_message'] = f"{current_player_obj['name']} was SKIPPED by user (UNSOLD for now)."

        # Log this action
        log_entry = {
            "bidder": "System",
            "info": f"Player {current_player_obj['name']} skipped by user. Marked as UNSOLD (pending AI simulation).",
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        }
        if 'bids_log' not in auction_runtime_state or not isinstance(auction_runtime_state['bids_log'], list):
            auction_runtime_state['bids_log'] = [log_entry]
        else:
            auction_runtime_state['bids_log'].append(log_entry)

        # Add to overall sold_players_history as UNSOLD for now
        sold_players_history = session.get('sold_players_history', [])
        sold_players_history.append({
            "name": current_player_obj['name'], "role": current_player_obj.get('role', 'N/A'),
            "price": 0, "team": "UNSOLD (Skipped)", "reason": "Skipped by User"
        })
        session['sold_players_history'] = sold_players_history

        session['auction_runtime_state'] = auction_runtime_state

    return redirect(url_for('auction_main'))

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
