// Replace this with your actual deployed FastAPI URL later
const BASE_URL = "https://fastapi-todo-app-6.onrender.com";
let currentFilter = 'all';
let allTodos = [];



function getAuthHeaders() {
    const token = localStorage.getItem("token");
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
    };
}

function showUser() {
    const name = localStorage.getItem("fullname");

    if (name) {
        document.getElementById("welcomeText").innerText = "Welcome, " + name;
    }
}
showUser();

// LOGOUT FUNCTION
function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("fullname");
    localStorage.removeItem("username");
    window.location.href = "login.html";
}

// TOAST NOTIFICATIONS
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        info: 'fa-info-circle'
    }[type] || 'fa-info-circle';

    toast.innerHTML = `
        <i class="fas ${icon}"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('toast-closing');
        toast.addEventListener('animationend', () => toast.remove());
    }, 3000);
}



// LOAD TODOS
async function getTodos() {
    try {
        const res = await fetch(`${BASE_URL}/TODOS`, {
            headers: getAuthHeaders()
        });

        const data = await res.json();
        allTodos = data.todos;
        renderTodos();
    } catch (error) {
        console.error("Error:", error);
        showToast("Failed to fetch tasks", "error");
    }
}

// RENDER TODOS
function renderTodos() {
    const list = document.getElementById("todoList");
    list.innerHTML = "";

    const filtered = allTodos.filter(todo => {
        if (currentFilter === 'pending') return !todo.completed;
        if (currentFilter === 'completed') return todo.completed;
        return true;
    });

    if (filtered.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <i class="fas ${currentFilter === 'completed' ? 'fa-clipboard-check' : 'fa-clipboard-list'}"></i>
                <p>${currentFilter === 'all' ? 'Your list is empty!' : 'No ' + currentFilter + ' tasks found.'}</p>
            </div>
        `;
        return;
    }

    filtered.forEach(todo => {
        const li = document.createElement("li");
        if (todo.completed) li.classList.add("completed");

        li.innerHTML = `
            <div class="todo-content">
                <div class="checkbox" onclick="toggleTodo(${todo.tid}, ${todo.completed}, '${todo.title.replace(/'/g, "\\'")}')"></div>
                <span class="todo-text">${todo.title}</span>
            </div>
            <div class="actions">
                <button class="action-btn edit-btn" onclick="editTodo(${todo.tid}, '${todo.title.replace(/'/g, "\\'")}', ${todo.completed})" title="Edit Task">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="action-btn delete-btn" onclick="deleteTodo(${todo.tid})" title="Delete Task">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;

        list.appendChild(li);
    });
}

// FILTERING
function setFilter(filter, btn) {
    currentFilter = filter;
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    renderTodos();
}

// ADD TODO
async function addTodo() {
    const input = document.getElementById("todoInput");
    const title = input.value.trim();

    if (!title) {
        showToast("Please enter a task!", "error");
        return;
    }

    try {
        const res = await fetch(`${BASE_URL}/TODOS`, {
            method: "POST",
            headers: getAuthHeaders(),   
            body: JSON.stringify({ title })
        });

        if (res.ok) {
            input.value = "";
            showToast("Task added successfully!", "success");
            getTodos();
        }
    } catch (error) {
        console.error("Error:", error);
        showToast("Error adding task", "error");
    }
}

// DELETE TODO
async function deleteTodo(id) {
    try {
        const res = await fetch(`${BASE_URL}/TODOS/${id}`, { method: "DELETE", headers: getAuthHeaders() });
        if (res.ok) {
            showToast("Task deleted", "info");
            getTodos();
        }
    } catch (error) {
        console.error("Error:", error);
        showToast("Error deleting task", "error");
    }
}

// TOGGLE COMPLETE
async function toggleTodo(id, currentStatus, title) {
    try {
        const res = await fetch(`${BASE_URL}/TODOS/${id}`, {
            method: "PUT",
            headers: getAuthHeaders(), 
            body: JSON.stringify({
                title: title,
                completed: !currentStatus
            })
        });

        if (res.ok) {
            showToast(currentStatus ? "Task marked as pending" : "Task completed! 🎉", "success");
            getTodos();
        }
    } catch (error) {
        console.error("Error:", error);
    }
}

// EDIT TODO
async function editTodo(id, oldTitle, completed) {
    const newTitle = prompt("Update your task:", oldTitle);
    
    if (newTitle === null || newTitle.trim() === "" || newTitle === oldTitle) return;

    try {
        const res = await fetch(`${BASE_URL}/TODOS/${id}`, {
            method: "PUT",
            headers: getAuthHeaders(),
            body: JSON.stringify({
                title: newTitle.trim(),
                completed: completed
            })
        });

        if (res.ok) {
            showToast("Task updated", "success");
            getTodos();
        }
    } catch (error) {
        console.error("Error:", error);
        showToast("Error updating task", "error");
    }
}

// Keyboard listener
document.getElementById("todoInput").addEventListener("keypress", (e) => {
    if (e.key === "Enter") addTodo();
});

// Initial load
getTodos();