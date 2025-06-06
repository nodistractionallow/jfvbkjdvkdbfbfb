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

# AuctionManager Helper Functions are removed as auction functionality is being disabled.
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
        # session['sold_players_history'] = [] # Removed: No longer used as auction summary page is removed

    except Exception as e:
        detailed_error = traceback.format_exc()
        # print(f"Error initializing game data: {e}\n{detailed_error}")
        return f"Error during game data initialization: {str(e)}. Check server logs. <a href='{url_for('index')}'>Back</a>"

    return redirect(url_for('choose_retention_mode'))

@app.route('/choose_retention_mode')
def choose_retention_mode():
    user_team_id = session.get('user_team_id')
    if not user_team_id:
        return redirect(url_for('index'))
    # In the next step, this will render 'choose_retention_mode.html'
    # For now, a placeholder response or render a minimal template:
    user_team_display_info = session.get('user_team_display_info', {})
    # return f"Placeholder for Choose Retention Mode. User team: {user_team_display_info.get('name', 'Unknown')}. Next step: create buttons."
    return render_template('choose_retention_mode.html', user_team_display_info=user_team_display_info)

@app.route('/retention') # This route now effectively becomes the retention form page
def retention_home():
    user_team_id = session.get('user_team_id')
    if not user_team_id: return redirect(url_for('index'))

    # Get retention mode selection from URL query param and store in session
    retention_mode_from_url = request.args.get('retention_mode_selection')
    if retention_mode_from_url and retention_mode_from_url in ['any', 'exact']:
        session['chosen_retention_mode'] = retention_mode_from_url

    chosen_mode = session.get('chosen_retention_mode')
    if not chosen_mode:
        # If no mode is set in session (e.g., direct navigation or after an error/clear session),
        # redirect to the mode selection page.
        return redirect(url_for('choose_retention_mode'))

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
                           user_team_budget=user_team_current_state.get('budget'),
                           chosen_retention_mode=chosen_mode) # Pass the chosen mode to the template

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
    # session['auction_runtime_state'] = {'current_player_index': -1} # Removed: No longer used as auction main page is removed

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

# Removed auction-related routes:
# - /auction (auction_main)
# - /auction/summary (auction_summary_page)
# - /auction/bid (auction_bid)
# - /auction_finalize_player (auction_finalize_player)

# Test initialization route (can be kept or removed)
# This route might still be useful for checking initial data loading
# independent of the auction flow.
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
