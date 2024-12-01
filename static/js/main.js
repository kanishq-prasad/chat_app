let socket;

// Initialize Socket.IO if on chat page
if (window.location.pathname.includes('/chat/')) {
    socket = io();
    
    socket.on('connect', () => { // the connect event in the frontend is a built-in event provided by the Socket.IO library. when the client connects to the server, this event is triggered automatically
        socket.emit('join', {
            room: ROOM_ID,
            user_id: USER_ID
        }); // the value of ROOM_ID and USERNAME are embeded in chat.html
        fetchMessages(USER_ID, ROOM_ID);
    });
    
    socket.on('message', (data) => {
        console.log('Message received:', data);
        appendMessage(data.username, data.message);
    });
    
    socket.on('status', (data) => {
        appendStatusMessage(data.msg);
    });
    
    socket.on('active_users', (data) => {
        updateActiveUsers(data.users);
    });
    
    // Handle page unload
    window.addEventListener('beforeunload', () => {
        socket.emit('leave', {
            room: ROOM_ID,
            user_id: USER_ID
        });
    });

    // Handle page reload
    window.addEventListener('unload', () => {
        socket.emit('leave', {
            room: ROOM_ID,
            user_id: USER_ID
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

function sendAuthenticatedRequest(route, method = 'GET') {
    const token = localStorage.getItem('token');
    const headers = {
        'Authorization': `Bearer ${token}`,
        'X-Requested-With': 'XMLHttpRequest'
    };

    return fetch(route, {
        method: method,
        headers: headers
    })
    .then(response => response.json())
    .catch(error => {
        console.error('Error:', error);
        throw error; // Re-throw the error to be handled by the caller
    });
}

function register() {
    const username = document.getElementById('username_r').value;
    // const email = document.getElementById('email').value;
    const password = document.getElementById('password_r').value;

    console.log("username: ", username);
    console.log("password: ", password);
    
    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Store token in localStorage
            localStorage.setItem('token', data.token);
            window.location.href = `/rooms/${data.user_id}`;
        } else {
            alert(data.message);
        }
    });
}

function login() {
    const username = document.getElementById('username_l').value;
    const password = document.getElementById('password_l').value;
    
    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Store token in localStorage
            localStorage.setItem('token', data.token);
            window.location.href = `/rooms/${data.user_id}`;
        } else {
            alert(data.message);
        }
    });
}

function setupAxiosInterceptors() {
    // Add token to all HTTP requests
    axios.interceptors.request.use(
        config => {
            const token = localStorage.getItem('token');
            if (token) {
                config.headers['Authorization'] = `Bearer ${token}`;
            }
            return config;
        },
        error => Promise.reject(error)
    );
}

function openRoom(user_id, roomID) {
    
    if (!roomID || !user_id) {
        alert('Invalid room code');
        return;
    }

    // console.log("roomID: ", roomID);
    
    window.location.href = `/chat/${user_id}/${roomID}`;
}

function addRoom(userID){

    console.log("userID: ", userID);

    if (!userID) {
        alert('No user ID found');
        return;
    }
    
    window.location.href = `/add-room/${userID}`;

}

function createRoom(userID) {
    // const username = document.getElementById('username').value;
    const roomID_Name = document.getElementById('roomID_Name').value;
    
    if (!userID || !roomID_Name) {
        alert('Please enter both username and room code');
        return;
    }
    
    fetch('/create-room', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_id: userID,
            roomName: roomID_Name
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // console.log("data.room_id: ", data.room_id);
            window.location.href = `/chat/${data.user_id}/${data.room_id}`;
        } else {
            alert(data.message);
        }
    });
}

function joinRoom(userID) {
    // const username = document.getElementById('username').value;
    const roomID_Name = document.getElementById('roomID_Name').value;
    
    if (!userID || !roomID_Name) {
        alert('Please enter both username and room code');
        return;
    }
    
    fetch('/join-room', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_id: userID,
            room_id: roomID_Name
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = `/chat/${data.user_id}/${data.room_id}`;
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
        user_id: USER_ID,
        message: message
    });

    // console.log("message: ", message, "ROOM_ID: ", ROOM_ID, "USER_ID: ", USER_ID);
    
    messageInput.value = '';
}

function leaveRoom() {
    socket.emit('leave', {
        room: ROOM_ID,
        user_id: USER_ID
    });

    window.location.href = `/rooms/${USER_ID}`;
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

function updateActiveUsers(users) {
    const userList = document.getElementById('activeUsers');
    if (userList) {
        userList.innerHTML = '';
    }
    Object.values(users).forEach(user => {
        const userElement = document.createElement('div');
        userElement.className = 'active-user';
        userElement.textContent = user.username || user; // Adjust based on the structure of user object
        userList.appendChild(userElement);
        console.log("user: ", user.username || user);
    });
}

// fetch the last 50 messages from the server
async function fetchMessages(user_id, room_id) {
    const response = await fetch(`/chat/${user_id}/${room_id}`);
    const messages = await response.json();
    const messagesList = document.getElementById('messages');
    messagesList.innerHTML = '';
    messages.forEach(msg => {
        const listItem = document.createElement('li');
        listItem.textContent = `${msg.user}: ${msg.message} (${new Date(msg.timestamp).toLocaleString()})`;
        messagesList.appendChild(listItem);
    });
}