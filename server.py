""" #bootstrap

We are writing a 2048 game with a backend in Python and Web frontend.

Our API is at /game and it has a simple interface:

- When the server starts, we initialize a new game
- A GET of /game always just returns the HTML for the current state of the game
- A GET of /game?move=u (with u, d, l, r according to the actual move) updates the game; the same request returns HTML for the div#game

For now we only run the Python backend locally and serve both index.html and the API on localhost.
In the JS we can just access the API by relative URI (as "/game").

We will listen on all interfaces (0.0.0.0) and port 8080.

Our HTML looks like this:

```html
<div id=game>
<div class="tile tile-empty"></div>
<div class="tile tile-empty"></div>
<div class="tile tile-1">2</div>
<div class="tile tile-empty"></div>
<div class="tile tile-empty"></div>
<div class="tile tile-2">4</div>
<div class="tile tile-empty"></div>
<div class="tile tile-empty"></div>
<div class="tile tile-empty"></div>
<div class="tile tile-empty"></div>
<div class="tile tile-empty"></div>
<div class="tile tile-empty"></div>
<div class="tile tile-empty"></div>
<div class="tile tile-empty"></div>
<div class="tile tile-empty"></div>
<div class="tile tile-empty"></div>
</div>
```

By "position index" we express the relationship between array indices and positions that we illustrate thusly:

```
 0  1  2  3
 4  5  6  7
 8  9 10 11
12 13 14 15
```

Thus in the example board above the 2 and 4 tiles are at index 2 and 5.

Our representation uses the log of the tile value in the array, for example here is our sample board above:

(Since we are writing Python these are lists, but we also use the term array for convenience.)

```python
[0,0,1,0,0,2,0,0,0,0,0,0,0,0,0,0]
```

We also use this log representations for things like CSS class names.
So "tile-1" means the tile with value 2^1, and "tile-17" is the highest-valued tile possible in the game.
This keeps our CSS and HTML a bit shorter and we only print the big numbers where necessary.

To communicate between the input layer and game mechanics, we use "u", "d", "l", "r" to identify the moves that the player can make in the game.

Code we already have:

- setup_game - returns initial random game representation
- board - takes game representation into HTML string
- game_update - takes game representation and move into new representation

Reply with "OK".
"""

"""
In setup_game we initialize and return the game structure, which is just an array of 16 ints.

There are two random tiles in the initial game state.

First we select two random distinct indices for the tiles, and then for each we pick a 2 with probability .9 or a 4 with probability .1.
"""

import random

def setup_game():
    game = [0] * 16
    indices = random.sample(range(16), 2)
    for index in indices:
        game[index] = 1 if random.random() < 0.9 else 2
    return game

""" board()

In board() we get our game representation and return an HTML string containing div#game.
"""

def board(game_rep):
    html = '<div id=game>'
    for val in game_rep:
        class_name = f'tile tile-{val}' if val > 0 else 'tile tile-empty'
        tile_value = str(2**val) if val > 0 else ''
        html += f'<div class="{class_name}">{tile_value}</div>'
    html += '</div>'
    return html

""" #handle_move_4cell
In hande_move_4cell, we get 4 ints representing either a row or column and handle the intra-row part of the move.

The elements are always already ordered such that we want to move to the left (i.e. towards lower indices).

1. Tiles slide in the direction of the move as far as they can until stopped by another tile or the edge of the board.
2. Tiles which are adjacent in the direction of the move and have the same value are then merged.
3. When multiple merges are possible, the rules are:
  - A merge which is furthest in the direction of motion is prioritized.
    For example, in a row [2 2 2 0] moving to the left, the result would be [4 2 0 0], not [2 4 0 0].
  - When both pairs in a row can merge, both merges are made, e.g. [2 2 2 2] -> [4 4 0 0] and [2 2 4 4] -> [4 8 0 0].

When we merge, since our board stores exponents (i.e. an 8 tile is stored as 3) and not tile values directly, we just add one to the exponent, rather than doubling it as we would do if we stored the actual power of two.

We first do a move to the left of anything non-zero.
Then we handle merges, by merging non-zero and equal adjacent tiles towards the left, incrementing on the left and zeroing on the right.
Finally we move anything non-zero to the left again to close any gaps caused by merging.
"""

def handle_move_4cell(cells):
    def move_non_zero_left(cells):
        new_cells = [c for c in cells if c != 0]
        return new_cells + [0] * (4 - len(new_cells))

    def merge_cells(cells):
        for i in range(3):
            if cells[i] != 0 and cells[i] == cells[i + 1]:
                cells[i] += 1
                cells[i + 1] = 0
        return cells

    cells = move_non_zero_left(cells)
    cells = merge_cells(cells)
    cells = move_non_zero_left(cells)
    return cells

""" #game_update

In game_update() we take a board and a direction, and perform the update according to the rules of 2048, specifically:

1. Tiles slide in the direction of the move as far as they can until stopped by another tile or the edge of the board.
2. Tiles which are adjacent in the direction of the move and have the same value are then merged.
3. When multiple merges are possible, the rules are:
  - A merge which is furthest in the direction of motion is prioritized.
    For example, in a row [2 2 2 0] moving to the left, the result would be [4 2 0 0], not [2 4 0 0].
  - When both pairs in a row can merge, both merges are made, e.g. [2 2 2 2] -> [4 4 0 0] and [2 2 4 4] -> [4 8 0 0].

In game_update we extract each row or column in a particular way from the board state which is passed in.
Then we call handle_move_4cell() with a length-4 array of those values, and that function always handles the transformation as if it was a row moving to the left.

We handle all four directions analogously.

We copy the "position index" table given above into the comment.
In the code below, rather than doing arithmetic with rows and columns, we simply include a nested list structure with ints between 0 and 15 that is easy to check for correctness.
We always value correctness over cleverness.

We can see that, for example, if the move is "d", we will call handle_move_4cell() with the array values from the board at indices [12 8 4 0], [13 9 5 1], and so on for all four columns.

Finally at the end of game_update we call add_new_tile with the previous and new board state and return the result.
"""

def game_update(board, move):
    direction_indices = {
        'u': [[0, 4, 8, 12], [1, 5, 9, 13], [2, 6, 10, 14], [3, 7, 11, 15]],
        'd': [[12, 8, 4, 0], [13, 9, 5, 1], [14, 10, 6, 2], [15, 11, 7, 3]],
        'l': [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], [12, 13, 14, 15]],
        'r': [[3, 2, 1, 0], [7, 6, 5, 4], [11, 10, 9, 8], [15, 14, 13, 12]]
    }
    new_board = board.copy()
    changed = False
    for indices in direction_indices[move]:
        original_values = [board[i] for i in indices]
        new_values = handle_move_4cell(original_values)
        if new_values != original_values:
            changed = True
            for i, value in zip(indices, new_values):
                new_board[i] = value
    if changed:
        new_board = add_new_tile(board, new_board)
    return new_board

"""
In add_new_tile() we get two boards in the usual format.

First we compare the two boards.
These are the board before and after a move.
If the board didn't change we just return the second board.

We find all the empty tiles, pick one uniformly at random, and add a new tile there (that is, actually a 1 in the board representation).
(Note that if the move did something, there will always be at least one empty spot.)

The new tile will be 2 or 4 with odds 9 : 1, just as in the initial game setup.
"""

import random

def add_new_tile(board_before, board_after):
    if board_before == board_after:
        return board_after
    empty_tiles = [i for i, tile in enumerate(board_after) if tile == 0]
    new_tile_value = 1 if random.random() < 0.9 else 2
    new_tile_position = random.choice(empty_tiles)
    board_after[new_tile_position] = new_tile_value
    return board_after

""" #server

Here we set up our server, using the standard Python HTTP server.

We call setup_game and put the game state in a variable.

We call board() with the current game state whenever we need the result for a GET.

When we get a move from the frontend, we update the game state (and we also still reply with the HTML for the board).

Here we handle:
- the /game endpoint
- serving index.html, 2048.css, and 2048.js from static files on disk with the same names; we serve index.html under "/"
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse as urlparse

game_state = setup_game()

class RequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type='text/html'):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        url_path = urlparse.urlparse(self.path).path
        query_components = urlparse.parse_qs(urlparse.urlparse(self.path).query)
        if url_path == '/game':
            move = query_components.get('move')
            if move:
                global game_state
                game_state = game_update(game_state, move[0])
            self._set_headers()
            self.wfile.write(board(game_state).encode())
        elif url_path == '/':
            self._set_headers()
            with open('index.html', 'rb') as file:
                self.wfile.write(file.read())
        elif url_path in ['/2048.css', '/2048.js']:
            content_type = 'text/css' if url_path.endswith('.css') else 'application/javascript'
            self._set_headers(content_type)
            with open(url_path[1:], 'rb') as file:
                self.wfile.write(file.read())

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    server_address = ('0.0.0.0', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd on port {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()

