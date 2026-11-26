fetch('/api/profile')
    .then(response => response.json())
    .then (data => {
        let nome = document.getElementById('nome')
        let minutos = document.getElementById('minutes')
        nome.textContent = data.name
        minutos.textContent = data.minutes

        const topArtistsList = document.getElementById('top_artists')
        const topTracksList = document.getElementById('top_tracks')
        if (data.top_artists.length === 0 ){
            topArtistsList.textContent = 'Ainda sem dados. Você já ouviu sua primeira música?'
        }
        if (data.top_tracks.length === 0 ){
            topTracksList.textContent = 'Ainda sem dados. Você já ouviu sua primeira música?'
        }
        for (let artist of data.top_artists) {
            const li = document.createElement('li')
            li.textContent = artist
            topArtistsList.appendChild(li)
        }
        for (let track of data.top_tracks) {
            const li = document.createElement('li')
            li.textContent = `${track.artist} - ${track.track}`
            topTracksList.appendChild(li)
        }

    })