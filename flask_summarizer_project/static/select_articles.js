// Add any JavaScript functionality here, such as:
// - Handling article selection
// - Sending selected articles to the server
// - Updating the UI based on user interactions

// Example: Selecting articles
const selectButtons = document.querySelectorAll('.select-article-btn');
const selectedArticles = [];

selectButtons.forEach(button => {
    button.addEventListener('click', () => {
        const row = button.parentNode.parentNode;
        const title = row.querySelector('td:first-child').textContent;
        // Basic selection logic - you'll likely want to adapt this
        if (selectedArticles.includes(title)) {
            selectedArticles.remove(title);
            button.textContent = '+';
        } else {
            selectedArticles.push(title);
            button.textContent = '✓';
        }

        console.log('Selected Articles:', selectedArticles);
    });
});

// Example: Sending selected articles to the server (you'll need to adapt this)
const generateSummaryButton = document.querySelector('.generate-summary-btn');
generateSummaryButton.addEventListener('click', () => {
    //  Fetch or other AJAX method to send selectedArticles to server
    fetch('/generate_summary', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ articles: selectedArticles })
    })
    .then(response => response.json())
    .then(data => {
        // Handle server response (e.g., redirect to results page)
        console.log('Server Response:', data);
        window.location.href = '/results'; // Example redirect
    })
    .catch(error => {
        console.error('Error:', error);
    });
});