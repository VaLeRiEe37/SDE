const messageForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message');
const chatHistory = document.getElementById('chat-history');

messageForm.addEventListener('submit', (event) => {
  event.preventDefault(); // Prevent default form submission behavior

  const message = messageInput.value;
  messageInput.value = ''; // Clear input field after sending

  fetch('/pawconnect/chatbot', {  // chat view URL
    method: 'POST',
    body: JSON.stringify({ message: message })
  })
  .then(response => response.json())
  .then(data => {
    chatHistory.innerHTML += `<p>You: ${message}</p><p>Chatbot: ${data.response}</p>`;
  })
  .catch(error => console.error(error));
});
