/* input handling

Here we update the board with the output from the backend, and handle input from the arrow keys.

We update the board once when the code first runs, and again after every move.
We are pulled in here from a script element at the end of the body, so no need for any DOMContentLoaded or other noise, we can just grab div#game directly.
*/

document.addEventListener('keydown', function(event) {
    let move = '';
    switch (event.key) {
        case 'ArrowUp': move = 'u'; break;
        case 'ArrowDown': move = 'd'; break;
        case 'ArrowLeft': move = 'l'; break;
        case 'ArrowRight': move = 'r'; break;
    }
    if (move) {
        fetch(`/game?move=${move}`)
        .then(response => response.text())
        .then(html => {
            document.getElementById('game').innerHTML = html;
        });
    }
});

fetch('/game')
.then(response => response.text())
.then(html => {
    document.getElementById('game').innerHTML = html;
});

