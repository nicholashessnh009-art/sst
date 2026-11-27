const sidebar = document.getElementById('sidebar');

function toggleSidebar() {
    sidebar.classList.toggle('aberta');
}
document.getElementById('avatar').src = 'static/style/img/user-avatar-filled.svg'

fetch('/api/me')
    .then(response => response.json())
    .then (data => {
        ;
        document.getElementById('close-sidebar').addEventListener('click', toggleSidebar);
        if (!data.logged_in) {
            document.getElementById('avatar').src = 'static/style/img/user-avatar-filled.svg'
            document.getElementById('avatar-btn').addEventListener('click', () => {
                window.location.href = '/login'
            })
            return
        }
        else {
            document.getElementById('avatar-btn').addEventListener('click', toggleSidebar)
        }
        document.getElementById('avatar').src = data.pfp || 'static/style/img/user-avatar-filled.svg'
        document.getElementById('avatar2').src = data.pfp || 'static/style/img/user-avatar-filled.svg'
        document.getElementById('sidebar-username').textContent = data.name

    })