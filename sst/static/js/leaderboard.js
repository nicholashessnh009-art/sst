fetch('/api/leaderboard')
    .then(response => response.json())
    .then(data => {
        const rankingList = document.getElementById('ranking-list')
        const topArtistsList = document.getElementById('top-artists-list')
        if (data.ranking.length === 0 ){
            rankingList.textContent = 'Ainda sem dados. Parece que ninguém escutou nada ainda... :/'
        }
        if (data.top_artists.length === 0 ){
            topArtistsList.textContent = 'Ainda sem dados. Parece que ninguém escutou nada ainda... :/'
        }
        for (let user of data.ranking) {
            const li = document.createElement('li')
            li.textContent = `${user.name} - ${user.minutes} minutos`
            rankingList.appendChild(li)
        }
        for (let artista of data.top_artists) {
            const li = document.createElement('li')
            li.textContent = `${artista.artist} - ${artista.times_played} reproduções`
            topArtistsList.appendChild(li)
        }
    })