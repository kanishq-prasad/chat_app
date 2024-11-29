function register() {
    const username = document.getElementById('username').value;
    // const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
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
            // Redirect to room creation/joining page
            window.location.href = `/rooms/${data.user_id}`;
        } else {
            alert(data.message);
        }
    });
}

function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
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
            // Redirect to room creation/joining page
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