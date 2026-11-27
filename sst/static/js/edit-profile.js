fetch('/api/me')
    .then(response => response.json())
    .then(data => {
        const contentDiv = document.getElementById('content')
        const loadingDiv = document.getElementById('carregando')
        const userElement = document.getElementById('ep-user')
        locationSelect = document.getElementById('location-select')
        if (data.location) {
            locationSelect.value = data.location
        }
        userElement.textContent = data.name
        contentDiv.classList.remove('hidden')
        loadingDiv.style.display = 'none'
        
    })