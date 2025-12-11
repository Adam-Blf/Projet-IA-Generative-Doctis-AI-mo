document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('triageForm');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const emptyState = document.getElementById('emptyState');
    const resultDiv = document.getElementById('analysisResult');
    const output = document.getElementById('markdownOutput');
    const sourcesList = document.getElementById('sourcesList');
    const themeToggle = document.getElementById('themeToggle');

    // Constants
    const ANIMATION_DURATION = 300;
    const TOAST_DURATION = 3000;

    // API Configuration
    // If we are on localhost, assume backend is on port 8000.
    // If on Vercel (Prod), use the environment variable or a hardcoded fallback until configured.
    // Ideally, Vercel injects this, but since we are static HTML, we might need a config.js or simple detection.

    // Simple Heuristic:
    const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    // CORRECT BACKEND URL from User
    const API_BASE_URL = isLocal ? 'http://localhost:8000' : 'https://doctis-aimo.onrender.com';

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
            first_name: document.getElementById('firstName').value,
            last_name: document.getElementById('lastName').value,
            age: parseInt(document.getElementById('age').value),
            gender: document.getElementById('gender').value,
            height: parseInt(document.getElementById('height').value),
            weight: parseInt(document.getElementById('weight').value),
            symptoms: document.getElementById('symptoms').value,
            // Optional fields
            history: document.getElementById('history').value || null,
            vitals: document.getElementById('vitals').value || null,
            medications: document.getElementById('medications').value || null
        };

        if (!payload.first_name || !payload.last_name || !payload.height || !payload.weight) {
            showToast('Veuillez remplir les champs obligatoires (Identité & Biométrie).', 'error');
            setLoading(false);
            return;
        }

        if (!payload.symptoms) {
            showToast('Veuillez décrire les symptômes.', 'error');
            setLoading(false);
            return;
        }

        try {
            console.log("Calling API at:", `${API_BASE_URL}/api/analyze`); // DEBUG
            // 3. API Call
            const response = await fetch(`${API_BASE_URL}/api/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Erreur serveur (${response.status}): ${errorText}`);
            }
            const responseData = await response.json();

            // 4. Render Results
            renderMarkdown(responseData.analysis);
            renderSources(responseData.sources);

            // 5. Switch Views
            emptyState.classList.add('hidden');
            resultDiv.classList.remove('hidden');

            showToast('Analyse terminée avec succès !', 'success');

        } catch (error) {
            console.error(error);
            showToast('Erreur API : ' + error.message, 'error');
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

        // Secure XSS: Use textContent for message, innerHTML only for trusted icon structure
        const iconSpan = document.createElement('span');
        iconSpan.textContent = icon;

        const messageDiv = document.createElement('div');
        messageDiv.textContent = message;

        toast.appendChild(iconSpan);
        toast.appendChild(messageDiv);

        container.appendChild(toast);

        // Remove after delay
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), ANIMATION_DURATION);
        }, TOAST_DURATION);
    }

    function setLoading(isLoading) {
        const spinner = analyzeBtn.querySelector('.spinner');
        const text = analyzeBtn.querySelector('.btn-text');

        if (isLoading) {
            spinner.classList.remove('hidden');
            text.textContent = 'Analyse en cours...';
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
        // Note: marked.parse returns HTML. In a prod env, use DOMPurify to sanitize cleanText/generated HTML.
        output.innerHTML = marked.parse(cleanText);
    }

    function renderSources(sources) {
        // Using map with template literals is cleaner, but potential XSS if source content is user-generated.
        // Assuming RAG sources are trusted (internal CSV). 
        sourcesList.innerHTML = sources.map(s => {
            // Escape simplistic approach if needed, or rely on trusted source.
            return `
            <div class="source-item">
                <strong>${s.disease}</strong> <small>(Sim: ${(s.score * 100).toFixed(0)}%)</small><br>
                ${s.description}
            </div>
            `;
        }).join('');
    }
});

function switchTab(tab) {
    // We can use the global showToast now if we expose it or just alert for now
    alert("Module 'Seconde Opinion' sera disponible en v2.1 !");
}
