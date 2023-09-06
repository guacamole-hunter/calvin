
function sendMessage() {
    let message = document.getElementById('userInput').value;
    fetch('/api/sendMessage', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        let chatbox = document.getElementById('chatbox');
        chatbox.innerHTML += `<p><strong>User:</strong> ${message}</p>`;
        chatbox.innerHTML += `<p><strong>Calvin:</strong> ${data.response}</p>`;
        if (data.manualKey) {
            chatbox.innerHTML += `<p><a href="./Manuals/${data.manualKey}" target="_blank">Refer to the manual</a></p>`;
        }
        document.getElementById('userInput').value = '';  // Clear the input field
    });
}
