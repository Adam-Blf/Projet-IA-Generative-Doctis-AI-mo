// State
let currentLang = 'fr';

// DOM Elements
const severityInput = document.getElementById('severity');
const severityVal = document.getElementById('severity-val');
const descInput = document.getElementById('description');
const charCount = document.getElementById('char-count');
const loadingSpinner = document.getElementById('loading-spinner');
const resultsArea = document.getElementById('results-area');
const analysisContent = document.getElementById('analysis-content');
const matchesList = document.getElementById('matches-list');
const ragAdvice = document.getElementById('rag-advice');

// Init
document.addEventListener('DOMContentLoaded', () => {
    updateTranslations();
});

// Event Listeners
severityInput.addEventListener('input', (e) => {
    updateSeverityVal(e.target.value);
});

descInput.addEventListener('input', (e) => {
    const len = e.target.value.length;
    charCount.textContent = len;
    if (len > 1000) {
        charCount.style.color = 'red';
    } else {
        charCount.style.color = '#777';
    }
});

// Functions
function updateSeverityVal(val) {
    severityVal.textContent = val;
}

function setLanguage(lang) {
    currentLang = lang;

    // Update active button
    document.querySelectorAll('.lang-btn').forEach(btn => btn.classList.remove('active'));
    // Simple logic, assuming button order Matches hardcoded logic or passing 'this' would be better but this works
    const btnIndex = lang === 'en' ? 0 : (lang === 'fr' ? 1 : 2);
    document.querySelectorAll('.lang-btn')[btnIndex].classList.add('active');

    updateTranslations();
}

function updateTranslations() {
    const t = translations[currentLang];
    document.getElementById('lbl_symptom_header').textContent = t.lbl_symptom_header;
    document.getElementById('lbl_severity').textContent = t.lbl_severity;
    document.getElementById('lbl_desc').textContent = t.lbl_desc;
    document.getElementById('lbl_results').textContent = t.lbl_results;
    document.getElementById('analyze-btn').textContent = t.btn_analyze;
    document.getElementById('description').placeholder = t.placeholder_desc;
    document.querySelector('#loading-spinner p').textContent = t.loading_text;
}

async function analyzeSymptoms() {
    const desc = descInput.value.trim();
    if (!desc) {
        alert("Please enter symptom details.");
        return;
    }

    // UI State: Loading
    resultsArea.classList.remove('hidden');
    loadingSpinner.classList.remove('hidden');
    analysisContent.classList.add('hidden');

    // Prepare Payload
    const payload = {
        description: desc,
        severity: severityInput.value,
        lang: currentLang
    };

    try {
        const response = await fetch('/api/triage', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        const data = await response.json();

        // Render Results
        renderResults(data);

    } catch (error) {
        console.error("Analysis Failed", error);
        alert("Service busy or offline. Please try again.");
    } finally {
        loadingSpinner.classList.add('hidden');
    }
}

function renderResults(data) {
    analysisContent.classList.remove('hidden');

    // RAG Advice
    ragAdvice.textContent = data.advice;

    // Matches
    matchesList.innerHTML = '';
    data.matches.forEach(match => {
        const li = document.createElement('li');

        let badgeClass = 'score-low';
        if (match.probability === 'High') badgeClass = 'score-high';
        if (match.probability === 'Moderate') badgeClass = 'score-moderate';

        // Format Score as Percentage
        const pct = Math.round(match.score * 100);

        li.innerHTML = `
            <span class="disease-name">${match.name}</span>
            <span class="score-badge ${badgeClass}">${pct}% Match (${match.probability})</span>
        `;
        matchesList.appendChild(li);
    });
}
