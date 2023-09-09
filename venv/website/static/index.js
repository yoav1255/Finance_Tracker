function deleteWatchlist(symbol_id) {
    fetch('/delete-watchlist', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ symbol_id: symbol_id }),
    })
    .then((_res) => {
        window.location.href = '/';
    })
    .catch((error) => {
        console.error('Error deleting symbol:', error);
    });
}

function deletePortfolio(symbol_id) {
    fetch('/delete-portfolio', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ symbol_id: symbol_id }),
    })
    .then((_res) => {
        window.location.href = '/portfolio';
    })
    .catch((error) => {
        console.error('Error deleting symbol:', error);
    });
}

function deleteHolding(holding_id) {
    fetch('/delete-holding', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ holding_id: holding_id }),
    })
    .then((_res) => {
        window.location.href = '/portfolio';
    })
    .catch((error) => {
        console.error('Error deleting symbol:', error);
    });
}
