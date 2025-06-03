from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Initialize the board
board = [' ' for _ in range(9)]
current_player = 'X'
game_over = False
winner = None
winning_condition = None
ai_mode = False
ai_player = 'O'

def check_winner():
    global winner, game_over, winning_condition
    win_conditions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Horizontal wins
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Vertical wins
        [0, 4, 8], [2, 4, 6]             # Diagonal wins
    ]
    for condition in win_conditions:
        if board[condition[0]] == board[condition[1]] == board[condition[2]] != ' ':
            winner = board[condition[0]]
            winning_condition = condition
            game_over = True
            return
    if ' ' not in board:
        game_over = True

def get_available_moves():
    return [i for i, cell in enumerate(board) if cell == ' ']

def minimax(board_state, depth, is_maximizing, alpha=-float('inf'), beta=float('inf')):
    # Check for terminal states
    temp_board = board[:]
    temp_winner = None
    temp_game_over = False
    
    # Check winner for current board state
    win_conditions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    
    for condition in win_conditions:
        if board_state[condition[0]] == board_state[condition[1]] == board_state[condition[2]] != ' ':
            temp_winner = board_state[condition[0]]
            temp_game_over = True
            break
    
    if not temp_game_over and ' ' not in board_state:
        temp_game_over = True
    
    # Return scores for terminal states
    if temp_game_over:
        if temp_winner == ai_player:
            return 10 - depth
        elif temp_winner:
            return depth - 10
        else:
            return 0
    
    if is_maximizing:
        max_eval = -float('inf')
        for i in range(9):
            if board_state[i] == ' ':
                board_state[i] = ai_player
                eval_score = minimax(board_state, depth + 1, False, alpha, beta)
                board_state[i] = ' '
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
        return max_eval
    else:
        min_eval = float('inf')
        human_player = 'X' if ai_player == 'O' else 'O'
        for i in range(9):
            if board_state[i] == ' ':
                board_state[i] = human_player
                eval_score = minimax(board_state, depth + 1, True, alpha, beta)
                board_state[i] = ' '
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
        return min_eval

def get_ai_move():
    available_moves = get_available_moves()
    if not available_moves:
        return None
    
    # Use minimax algorithm to find the best move
    best_score = -float('inf')
    best_move = available_moves[0]
    
    for move in available_moves:
        board_copy = board[:]
        board_copy[move] = ai_player
        score = minimax(board_copy, 0, False)
        if score > best_score:
            best_score = score
            best_move = move
    
    return best_move

@app.route('/')
def index():
    global board, current_player, game_over, winner, winning_condition, ai_mode
    # Reset the game state when the page is loaded
    board = [' ' for _ in range(9)]
    current_player = 'X'
    game_over = False
    winner = None
    winning_condition = None
    ai_mode = False
    return render_template('index.html', board=board, current_player=current_player, game_over=game_over, winner=winner, winning_condition=winning_condition, ai_mode=ai_mode)

@app.route('/set_mode', methods=['POST'])
def set_mode():
    global ai_mode, board, current_player, game_over, winner, winning_condition
    ai_mode = request.form.get('ai_mode') == 'true'
    # Reset the game when mode changes
    board = [' ' for _ in range(9)]
    current_player = 'X'
    game_over = False
    winner = None
    winning_condition = None
    return jsonify({'success': True, 'ai_mode': ai_mode})

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
                
                # If AI mode is enabled and it's AI's turn, make AI move
                if ai_mode and current_player == ai_player and not game_over:
                    ai_move = get_ai_move()
                    if ai_move is not None:
                        board[ai_move] = ai_player
                        check_winner()
                        if not game_over:
                            current_player = 'X' if current_player == 'O' else 'O'
    
    return jsonify({
        'board': board, 
        'currentPlayer': current_player, 
        'gameOver': game_over, 
        'winner': winner, 
        'winningCondition': winning_condition,
        'aiMode': ai_mode
    })

# Export the Flask app for Vercel
app = app
