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
        if (data.top_artist_image.length > 0) {

            const image_url = data.top_artist_image[0]
            let image = document.createElement('img')
            let label = document.getElementById('top-artist-image-header')
            image.src = image_url
            label.textContent = `Você é superfã de ${data.top_artists[0]}!`
            image.alt = `Você é superfã de ${data.top_artists[0]}!`
            image.title = `${data.top_artists[0]}`
            const imageContainer = document.getElementById('profile-top-artist-image')
            imageContainer.appendChild(image)
            image.style.borderRadius = '50%'
            image.style.aspectRatio = '1 / 1'
        }
        else {
            const imageContainer = document.getElementById('profile-top-artist-image')
            
        }
        const accountAgeElement = document.getElementById('age')
        if (data.account_age_days == undefined) {
            accountAgeElement.textContent = 'Sem dados'
        }
        else {
            accountAgeElement.textContent = `${data.account_age_days + 1} dias`
        }
        document.getElementById('carregando').style.display = 'none'
        document.getElementById('content').classList.remove('hidden')
    })