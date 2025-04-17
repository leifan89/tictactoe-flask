from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Initialize the board
board = [' ' for _ in range(9)]
current_player = 'X'
game_over = False
winner = None

def check_winner():
    global winner, game_over
    win_conditions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Horizontal wins
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Vertical wins
        [0, 4, 8], [2, 4, 6]             # Diagonal wins
    ]
    for condition in win_conditions:
        if board[condition[0]] == board[condition[1]] == board[condition[2]] != ' ':
            winner = board[condition[0]]
            game_over = True
            return
    if ' ' not in board:
        game_over = True

@app.route('/')
def index():
    global board, current_player, game_over, winner
    # Reset the game state when the page is loaded
    board = [' ' for _ in range(9)]
    current_player = 'X'
    game_over = False
    winner = None
    return render_template('index.html', board=board, current_player=current_player, game_over=game_over, winner=winner)

@app.route('/move', methods=['POST'])
def move():
    global board, current_player, game_over
    if not game_over:
        position = int(request.form['position'])
        if board[position] == ' ':
            board[position] = current_player
            check_winner()
            if not game_over:
                current_player = 'O' if current_player == 'X' else 'X'
    return jsonify({'board': board, 'currentPlayer': current_player, 'gameOver': game_over, 'winner': winner})

if __name__ == '__main__':
    app.run(debug=True)