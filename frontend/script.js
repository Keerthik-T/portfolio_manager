// Fetch model info on load
fetch(`${API_URL}/api/health`)
    .then(res => res.json())
    .then(data => {
        document.getElementById('modelBadge').innerHTML = `🤖 AI Model: ${data.model}`;
    });
