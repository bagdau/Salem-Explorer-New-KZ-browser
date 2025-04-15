const apiKey = 'СЕНІҢ_ЕБАТЬ_КІЛТІҢ';  // Вставьте ваш реальный ключ API сюда

async function fetchNews() {
    try {
        const response = await fetch(`https://newsapi.org/v2/top-headlines?country=ru&apiKey=${apiKey}`);
        const data = await response.json();
        
        if (data.status === 'ok' && data.articles.length > 0) {
            displayNews(data.articles);
        } else {
            newsContainer.innerHTML = '<p>Нет новостей для отображения.</p>';
        }
    } catch (error) {
        newsContainer.innerHTML = '<p>Ошибка при загрузке новостей. Пожалуйста, попробуйте снова.</p>';
        console.error('Ошибка загрузки новостей:', error);
    }
}
