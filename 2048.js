/*

We handle keyboard input from the arrow keys.

We are pulled in here from a script element at the end of the body, so we first get the div#game which is already in our HTML (so no need for any DOMContentLoaded or other noise).

*/

document.addEventListener('keydown', function(e) {
    let move = '';
    switch (e.key) {
        case 'ArrowUp':    move = 'u'; break;
        case 'ArrowDown':  move = 'd'; break;
        case 'ArrowLeft':  move = 'l'; break;
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

