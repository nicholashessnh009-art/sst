fetch('/api/leaderboard') // pega informações do servidor (ranking, artistas, etc)
    .then(response => response.json()) // converte a resposta em JSON
    .then(data => { // quando a resposta chega, executa essa função
        const rankingList = document.getElementById('ranking-list')
        const topArtistsList = document.getElementById('top-artists-list')
        const currentUser = data.me.name
        if (data.ranking.length === 0 ){
            rankingList.textContent = 'Ainda sem dados. Parece que ninguém escutou nada ainda... :/'
        }
        if (data.top_artists.length === 0 ){
            topArtistsList.textContent = 'Ainda sem dados. Parece que ninguém escutou nada ainda... :/'
        }
        for (let user of data.ranking) {
            const li = document.createElement('li')
            li.textContent = `${user.name} - ${user.minutes} minutos`
            li.classList.add('list-element')
            rankingList.appendChild(li)
            if (user.id === currentUser) {
                li.classList.add('voce')
            }
        }
        for (let artista of data.top_artists) {
            const li = document.createElement('li')
            li.textContent = `${artista.artist} - ${artista.times_played} reproduções`
            topArtistsList.appendChild(li)
        }
        document.getElementById('carregando').style.display = 'none'
        document.getElementById('content').classList.remove('hidden')
    })