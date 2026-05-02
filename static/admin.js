const BASE_URL = "https://fastapi-todo-app-6.onrender.com";

function getHeaders() {
    return {
        "Authorization": "Bearer " + localStorage.getItem("token")
    };
}


const role = localStorage.getItem("role");

if (role !== "admin") {
    alert("Access Denied");
    window.location.href = "static\index.html";
}


// Load dashboard
async function loadDashboard() {
    const res = await fetch(BASE_URL + "/admin/dashboard", {
        headers: getHeaders()
    });

    const data = await res.json();

    document.getElementById("totalUsers").innerText = data.total_users;
    document.getElementById("totalTodos").innerText = data.total_todos;
    document.getElementById("completedTodos").innerText = data.completed;
    document.getElementById("pendingTodos").innerText = data.pending;
}

// Load users
async function loadUsers() {
    const res = await fetch(BASE_URL + "/admin/users", {
        headers: getHeaders()
    });

    const users = await res.json();
    const table = document.getElementById("usersTable");

    table.innerHTML = "";

    users.forEach(user => {
        table.innerHTML += `
            <tr>
                <td>${user.id}</td>
                <td>${user.fullname}</td>
                <td>${user.username}</td>
                <td>
                    <button onclick="deleteUser(${user.id})">Delete</button>
                </td>
            </tr>
        `;
    });
}

// Load todos
async function loadTodos() {
    const res = await fetch(BASE_URL + "/admin/todos", {
        headers: getHeaders()
    });

    const todos = await res.json();
    const table = document.getElementById("todosTable");

    table.innerHTML = "";

    todos.forEach(todo => {
        table.innerHTML += `
            <tr>
                <td>${todo.tid}</td>
                <td>${todo.title}</td>
                <td>${todo.completed ? "✔" : "❌"}</td>
                <td>${todo.user_id}</td>
                <td>
                    <button onclick="deleteTodo(${todo.tid})">Delete</button>
                </td>
            </tr>
        `;
    });
}

// Delete user
async function deleteUser(id) {
    await fetch(`${BASE_URL}/admin/users/${id}`, {
        method: "DELETE",
        headers: getHeaders()
    });
    loadUsers();
}

// Delete todo
async function deleteTodo(id) {
    await fetch(`${BASE_URL}/admin/todos/${id}`, {
        method: "DELETE",
        headers: getHeaders()
    });
    loadTodos();
}

function logout() {
    localStorage.clear();
    window.location.href = "login.html";
}

// Init
loadDashboard();
loadUsers();
loadTodos();