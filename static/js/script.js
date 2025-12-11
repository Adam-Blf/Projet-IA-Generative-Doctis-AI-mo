document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('triageForm');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const emptyState = document.getElementById('emptyState');
    const resultDiv = document.getElementById('analysisResult');
    const output = document.getElementById('markdownOutput');
    const sourcesList = document.getElementById('sourcesList');
    const themeToggle = document.getElementById('themeToggle');

    // --- THEME MANAGEMENT ---
    const savedTheme = localStorage.getItem('theme') || 'dark'; // Default to dark
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    themeToggle.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        updateThemeIcon(next);
    });

    function updateThemeIcon(theme) {
        themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
    }

    // --- FORM LOGIC ---
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // 1. UI Loading State
        setLoading(true);

        // 2. Gather Data
        const payload = {
            age: parseInt(document.getElementById('age').value),
            gender: document.getElementById('gender').value,
            symptoms: document.getElementById('symptoms').value
        };

        if (!payload.symptoms) {
            showToast("Veuillez décrire les symptômes.", "error");
            setLoading(false);
            return;
        }

        try {
            // 3. API Call
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) throw new Error("Erreur serveur");
            const data = await response.json();

            // 4. Render Results
            renderMarkdown(data.analysis);
            renderSources(data.sources);

            // 5. Switch Views
            emptyState.classList.add('hidden');
            resultDiv.classList.remove('hidden');

            showToast("Analyse terminée avec succès !", "success");

        } catch (error) {
            console.error(error);
            showToast("Erreur API : " + error.message, "error");
        } finally {
            setLoading(false);
        }
    });

    // --- HELPERS ---
    function showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        let icon = 'ℹ️';
        if (type === 'error') icon = '❌';
        if (type === 'success') icon = '✅';

        toast.innerHTML = `<span>${icon}</span> <div>${message}</div>`;

        container.appendChild(toast);

        // Remove after 3s
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    function setLoading(isLoading) {
        const spinner = analyzeBtn.querySelector('.spinner');
        const text = analyzeBtn.querySelector('.btn-text');

        if (isLoading) {
            spinner.classList.remove('hidden');
            text.textContent = "Analyse en cours...";
            analyzeBtn.disabled = true;
        } else {
            spinner.classList.add('hidden');
            text.textContent = "Lancer l'Analyse";
            analyzeBtn.disabled = false;
        }
    }

    function renderMarkdown(text) {
        // Simple Markdown cleaning (remove JSON artifacts if any)
        const cleanText = text.replace(/```json/g, '').replace(/```/g, '');
        output.innerHTML = marked.parse(cleanText);
    }

    function renderSources(sources) {
        sourcesList.innerHTML = sources.map(s => `
            <div class="source-item">
                <strong>${s.disease}</strong> <small>(Sim: ${(s.score * 100).toFixed(0)}%)</small><br>
                ${s.description}
            </div>
        `).join('');
    }
});

function switchTab(tab) {
    // We can use the global showToast now if we expose it or just alert for now
    alert("Module 'Seconde Opinion' sera disponible en v2.1 !");
}
