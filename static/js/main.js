let socket;

// Initialize Socket.IO if on chat page
if (window.location.pathname.includes('/chat/')) {
    socket = io();
    
    socket.on('connect', () => { // the connect event in the frontend is a built-in event provided by the Socket.IO library. when the client connects to the server, this event is triggered automatically
        socket.emit('join', {
            room_id: ROOM_ID,
            username: USERNAME
        }); // the value of ROOM_ID and USERNAME are embeded in chat.html
        fetchMessages(ROOM_ID);
    });
    
    socket.on('message', (data) => {
        console.log('Message received:', data.message);
        appendMessage(data.username, data.message);
    });
    
    socket.on('status', (data) => {
        appendStatusMessage(data.msg);
    });
    
    // Handle page unload
    window.addEventListener('beforeunload', () => {
        socket.emit('leave', {
            room_id: ROOM_ID,
            username: USERNAME
        });
    });

    // Handle page reload
    window.addEventListener('unload', () => {
        socket.emit('leave', {
            room_id: ROOM_ID,
            username: USERNAME
        });
    });

    // Add event listener for Enter key in message input
    document.getElementById('messageInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Handle initial chat history
    socket.on('chat_history', (data) => {
    const messagesDiv = document.getElementById('messages');
    messagesDiv.innerHTML = ''; // Clear existing messages

    data.messages.forEach(msg => {
        appendMessage(msg);
    });

    // Scroll to bottom
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    });
}

function createRoom() {
    const username = document.getElementById('username').value;
    const roomID_Name = document.getElementById('roomID_Name').value;
    
    if (!username || !roomID_Name) {
        alert('Please enter both username and room code');
        return;
    }
    
    fetch('/create-room', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username,
            roomName: roomID_Name
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = `/chat/${data.room_id}`;
        } else {
            alert(data.message);
        }
    });
}

function joinRoom() {
    const username = document.getElementById('username').value;
    const roomID_Name = document.getElementById('roomID_Name').value;
    
    if (!username || !roomID_Name) {
        alert('Please enter both username and room code');
        return;
    }
    
    fetch('/join-room', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username,
            roomID: roomID_Name
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = `/chat/${roomID}`;
        } else {
            alert(data.message);
        }
    });
}

function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    
    if (!message) return;
    
    socket.emit('message', {
        room_id: ROOM_ID,
        username: USERNAME,
        message: message
    });
    
    messageInput.value = '';
}

function appendMessage(username, message, timestamp) {
    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    
    const timeSpan = document.createElement('span');
    timeSpan.className = 'timestamp';
    timeSpan.textContent = timestamp;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = `${username}: ${message}`;
    
    messageDiv.appendChild(timeSpan);
    messageDiv.appendChild(contentDiv);
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function appendStatusMessage(message) {
    const messagesDiv = document.getElementById('messages');
    const statusDiv = document.createElement('div');
    statusDiv.className = 'status-message';
    statusDiv.textContent = message;
    messagesDiv.appendChild(statusDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

socket.on('active_users', (data) => {
    updateActiveUsers(data.users);
});

function updateActiveUsers(users) {
    const userList = document.getElementById('activeUsers');
    if (userList) {
        userList.innerHTML = '';
        users.forEach(user => {
            const userElement = document.createElement('div');
            userElement.className = 'active-user';
            userElement.textContent = user;
            userList.appendChild(userElement);
        });
    }
}

// fetch the last 50 messages from the server
async function fetchMessages(room_id) {
    const response = await fetch(`/chat/${room_id}`);
    const messages = await response.json();
    const messagesList = document.getElementById('messages');
    messagesList.innerHTML = '';
    messages.forEach(msg => {
        const listItem = document.createElement('li');
        listItem.textContent = `${msg.user}: ${msg.message} (${new Date(msg.timestamp).toLocaleString()})`;
        messagesList.appendChild(listItem);
    });
}