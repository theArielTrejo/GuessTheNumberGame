from flask import Flask, render_template, request, redirect, url_for, jsonify
import random
import time

app = Flask(__name__)
game_rooms = {}  # Store rooms with code and usernames

# Routes you to the main page
@app.route('/')
def index():
    return render_template('index.html')


# Routes you to the create page
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        username = request.form['username']
        room_code = request.form['room_code']
        room_name = request.form['room_name']
        game_rooms[room_code] = {
            'room_name': room_name,
            'players': {username: {}},  # Create a dict to for all info needed for the game lobbies
            'host': username,
            'round_number': 1,  # Track the current round number
            'game_active': False, # Set to false to indicate game hasnt started, will be used to not allow people in games that started
            'survivors': []  # Track players who survived each round
        }
        # Redirects to the lobby to start the game
        return redirect(url_for('lobby', room_code=room_code, username=username))
    return render_template('create.html')

# Route to join webpage
@app.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == 'POST':
        username = request.form['username']
        room_code = request.form['room_code']
        if room_code in game_rooms:
            # Only allow joining if game hasn't started or player is rejoining after surviving
            if not game_rooms[room_code].get('game_active', False) or username in game_rooms[room_code].get('survivors',
                                                                                                            []):
                game_rooms[room_code]['players'][username] = {}
                return redirect(url_for('lobby', room_code=room_code, username=username))
            else:
                return "Game already in progress. Wait for the next round.", 403
        else:
            return "Room not found!", 404
    return render_template('join.html')

# Routes you to a lobby with the dedicated room code
@app.route('/lobby/<room_code>/<username>')
def lobby(room_code, username):
    room = game_rooms.get(room_code)
    if not room:
        return "Room not found!", 404
    # Check if player should be in this lobby
    if username != room['host'] and username not in room.get('survivors', []) and room.get('game_active', False):
        # You do not become a player once you get eliminated
        return redirect(url_for('eliminated', room_code=room_code, username=username))
    return render_template('lobby.html', room=room, username=username, room_code=room_code)

# Route to the eliminated webpage with dedicated lobby code
@app.route('/eliminated/<room_code>/<username>')
def eliminated(room_code, username):
    room = game_rooms.get(room_code)
    if not room:
        return "Room not found!", 404

    # Get the user's guess and the secret number
    user_guess = room['players'].get(username, {}).get('guess', 'unknown')
    secret_number = room.get('secret_number', 'unknown')

    return render_template('eliminated.html',
                           username=username,
                           guess=user_guess,
                           secret_number=secret_number,
                           room_code=room_code)

# This is to get the players info to display and to keep track of data
@app.route('/get_players/<room_code>')
def get_players(room_code):
    if room_code in game_rooms:
        return jsonify(list(game_rooms[room_code]['players'].keys()))
    else:
        return jsonify([])

# Route to start game
@app.route('/start_game/<room_code>', methods=['POST'])
def start_game(room_code):
    room = game_rooms.get(room_code)
    if not room:
        return "Room not found!", 404

    if room.get('game_active'):
        return "Game already started!", 400

    # Marks that game is starting just waiting for the host to enter their number
    room['game_setup'] = True
    room['game_active'] = True
    return jsonify({'message': 'Game setup started, waiting for host to enter the secret number.'})

# This route sets the secret number, needed to pass the information between each other
@app.route('/set_secret_number/<room_code>', methods=['POST'])
def set_secret_number(room_code):
    if room_code not in game_rooms:
        return jsonify({"error": "Room not found"}), 404

    secret_number = int(request.form.get('secret_number'))
    game_rooms[room_code]['secret_number'] = secret_number

    # Generate 8 random numbers (1-100) that are NOT the secret number
    options = set()
    while len(options) < 8:
        num = random.randint(1, 100)
        if num != secret_number:
            options.add(num)

    options = list(options)
    options.append(secret_number)  # Add the real secret number
    random.shuffle(options)  # Shuffle the 9 numbers

    game_rooms[room_code]['options'] = options
    game_rooms[room_code]['round_results'] = None
    game_rooms[room_code]['results_ready'] = False

    # Reset all player guesses for this round
    for player_name in game_rooms[room_code]['players']:
        if 'guess' in game_rooms[room_code]['players'][player_name]:
            game_rooms[room_code]['players'][player_name]['guess'] = None

    return jsonify({
        "message": f"Secret number set for round {game_rooms[room_code].get('round_number', 1)}!",
        "options": options  # Send back the 9 numbers to show buttons
    })

# Route to collect the numbers the players have entered
@app.route('/guess_number/<room_code>/<username>', methods=['POST'])
def guess_number(room_code, username):
    room = game_rooms.get(room_code)
    if not room:
        return jsonify({'error': 'Room not found'}), 404

    # Ensure players is a dictionary and contains the username
    if username not in room['players']:
        return jsonify({'error': 'Player not found'}), 404

    # Get the guess from form data
    guess = request.form.get('guess')
    if not guess:
        return jsonify({'error': 'No guess provided'}), 400

    # Record the player's guess
    room['players'][username]['guess'] = int(guess)

    # Check if all NON-HOST players have guessed
    non_host_players = [name for name in room['players'] if name != room['host']]
    all_guessed = all(
        room['players'][name].get('guess') is not None
        for name in non_host_players
    )

    # Store results if all non-host players have guessed
    if all_guessed:
        secret = room.get('secret_number')
        results = []
        survivors = []
        eliminated = []

        for name, info in room['players'].items():
            if name == room['host']:
                continue  # host doesn't guess

            player_guess = info.get('guess')
            if player_guess == secret:
                results.append(f"{name} guessed {player_guess} - Survives!")
                survivors.append(name)
            else:
                results.append(f"{name} guessed {player_guess} - Eliminated!")
                eliminated.append(name)

        room['round_results'] = "\n".join(results)
        room['survivors'] = survivors
        room['eliminated'] = eliminated
        room['results_ready'] = True

        # Check if there's only one survivor, the winner
        if len(survivors) == 1:
            room['winner'] = survivors[0]
            room['round_results'] += f"\n\n{survivors[0]} is the WINNER WOOHOO!"
        elif len(survivors) == 0:
            # No survivors, game over
            room['round_results'] += "\n\nNo survivors! Game over!"
        else:
            # Prepare for next round
            room['round_number'] = room.get('round_number', 1) + 1

    return jsonify({
        'message': 'Guess received!',
        'all_guessed': all_guessed
    })

# Get the data of the current game
@app.route('/get_game_data/<room_code>')
def get_game_data(room_code):
    room = game_rooms.get(room_code)
    if not room or 'options' not in room:
        return jsonify({'ready': False})
    return jsonify({'ready': True, 'options': room['options']})

# This collects the data of the round results. So it can be displayed
@app.route('/get_round_results/<room_code>')
def get_round_results(room_code):
    room = game_rooms.get(room_code)
    if not room:
        return jsonify({"results": None, "results_ready": False})

    return jsonify({
        "results": room.get("round_results"),
        "results_ready": room.get("results_ready", False),
        "survivors": room.get("survivors", []),
        "eliminated": room.get("eliminated", []),
        "winner": room.get("winner"),
        "round_number": room.get("round_number", 1)
    })

# This determines if the round has ended to start the next round
@app.route('/start_next_round/<room_code>', methods=['POST'])
def start_next_round(room_code):
    print(f"Start next round request received for room {room_code}")

    room = game_rooms.get(room_code)
    if not room:
        print(f"Room {room_code} not found")
        return jsonify({"error": "Room not found"}), 404

    # Only host can start next round
    requesting_user = request.form.get('username')
    print(f"Request from user: {requesting_user}, host is: {room.get('host')}")

    if requesting_user != room.get('host'):
        print(f"User {requesting_user} is not the host {room.get('host')}")
        return jsonify({"error": "Only the host can start the next round"}), 403

    # Reset for next round
    room['results_ready'] = False
    room['round_results'] = None
    room['winner'] = None

    # Clear previous guesses
    for player in room['players']:
        if 'guess' in room['players'][player]:
            room['players'][player]['guess'] = None

    #Debug
    print(f"Current survivors: {room.get('survivors', [])}")

    # Keep only survivors in the player list
    survivors = room.get('survivors', [])
    host = room.get('host')

    # Create a new player dictionary with only survivors and host
    updated_players = {host: room['players'][host]} if host in room['players'] else {}

    for player in survivors:
        if player in room['players']:
            updated_players[player] = room['players'][player]

    room['players'] = updated_players
    print(f"Updated player list: {list(room['players'].keys())}")

    # Reset survivors list for next round
    room['survivors'] = []
    room['eliminated'] = []

    # Make sure game is still marked as active
    room['game_active'] = True

    # Debug info
    print(f"Starting round {room.get('round_number', 1)} with players: {list(room['players'].keys())}")

    return jsonify({
        "message": f"Starting round {room.get('round_number', 1)}",
        "round_number": room.get('round_number', 1),
        "survivors": list(room['players'].keys()),
        "success": True
    })

# I used this to debug my json errors
@app.route('/debug_room/<room_code>')
def debug_room(room_code):
    """Debug endpoint to check room state"""
    room = game_rooms.get(room_code)
    if not room:
        return jsonify({"error": "Room not found"}), 404

    # Create a safe copy of room data
    safe_room = {}
    for key, value in room.items():
        if key == 'players':
            # Don't include all player details
            safe_room[key] = list(value.keys())
        else:
            safe_room[key] = value

    return jsonify({
        "room_code": room_code,
        "room_state": safe_room
    })

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port= 5003)