document.addEventListener('DOMContentLoaded', function() {

    // fetch newest chat sessions in chat list
    function fetchAndUpdateChatList() {
        // Check if we're actually on the 'my_chats' page
        if (!document.querySelector('.my-chat-list')) {
            return; // Exit if not on the 'my_chats' page
        }
        fetch(`/pawconnect/fetch_new_chats/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log(data); 
                const chatListContainer = document.querySelector('.my-chat-list');
                chatListContainer.innerHTML = ''; // Clear the list

                data.chat_sessions.forEach(session_info => {
                    const chatUrl = `/pawconnect/chat_with_user/${session_info.session_id}`;

                    const chatSessionDiv = document.createElement('div');
                    chatSessionDiv.className = 'my-chats-chat-session';
                    chatSessionDiv.innerHTML = `
                        <a href="${chatUrl}">
                            Chat with ${session_info.other_user_full_name}
                        </a>
                        ${session_info.unread_count ? `<span class="unread-messages">Unread Messages: ${session_info.unread_count}</span>` : ''}
                    `;
                    chatListContainer.appendChild(chatSessionDiv);
                });
            })
            .catch(error => {
                console.error('Error updating chat list:', error);
            });
    }
    // Call this function only if '.chat-list' exists on the page
    if (document.querySelector('.my-chat-list')) {
        fetchAndUpdateChatList();
        setInterval(fetchAndUpdateChatList, 5000); // Refresh every 5 seconds
    }

    // Function to fetch and update messages
    function fetchAndUpdateMessages() {
        // Check if we're actually on the 'chat_with_user' page
        const chatSessionElement = document.getElementById('chat-session-id');
        if (!chatSessionElement) {
            return; // Exit if not on the 'chat_with_user' page
        }

        const sessionId = document.getElementById('chat-session-id').value;
        fetch(`/pawconnect/fetch_new_messages/${sessionId}/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                const messagesContainer = document.getElementById('chat-messages');
                messagesContainer.innerHTML = ''; // Clear current messages and replace with new ones
                data.messages.forEach(message => {
                    const messageRow = document.createElement('div');
                    messageRow.className = `message-row ${message.is_sender ? 'message-sent' : 'message-received'}`;

                    const messageBubble = document.createElement('div');
                    messageBubble.className = 'message-bubble';
                    messageBubble.textContent = message.message;

                    const timestamp = document.createElement('span');
                    timestamp.className = 'timestamp';
                    // timestamp.textContent = new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true });
                    timestamp.textContent = new Date(message.timestamp + 'Z').toLocaleTimeString('en-US', {
                        hour: '2-digit', 
                        minute: '2-digit', 
                        hour12: true,
                        timeZone: 'America/New_York'
                    });

                    messageRow.appendChild(messageBubble);
                    messageRow.appendChild(timestamp);

                    messagesContainer.appendChild(messageRow);
                });
                // Scroll to the bottom of the chat messages container
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            })
            .catch(error => console.error('Error fetching messages:', error));
    }

    // Call this function only if '#chat-session-id' exists on the page
    if (document.getElementById('chat-session-id')) {
        fetchAndUpdateMessages();
        setInterval(fetchAndUpdateMessages, 5000); // Refresh every 5 seconds
    }
});