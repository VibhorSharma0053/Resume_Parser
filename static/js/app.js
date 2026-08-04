// static/js/app.js

// ── Get DOM Elements ───────────────────────────────────────────
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const removeFile = document.getElementById('removeFile');
const parseBtn = document.getElementById('parseBtn');

const uploadSection = document.querySelector('.upload-section');
const loadingSection = document.getElementById('loadingSection');
const errorSection = document.getElementById('errorSection');
const resultsSection = document.getElementById('resultsSection');

const tryAgainBtn = document.getElementById('tryAgainBtn');
const parseAnotherBtn = document.getElementById('parseAnotherBtn');
const copyJsonBtn = document.getElementById('copyJson');

// ── State ──────────────────────────────────────────────────────
let selectedFile = null;


// ── File Selection Helpers ─────────────────────────────────────

function formatFileSize(bytes) {
    /** Converts bytes to a readable string like "1.23 MB" */
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}

function handleFileSelect(file) {
    /**
     * Called when user selects or drops a file.
     * Shows file info and enables the parse button.
     */
    if (!file) return;

    // Check file type before even sending to server
    const allowed = ['.pdf', '.docx'];
    const ext = '.' + file.name.split('.').pop().toLowerCase();

    if (!allowed.includes(ext)) {
        showError(
            'INVALID_FILE_TYPE',
            `File type "${ext}" is not supported.`,
            'Please upload a PDF or DOCX file.'
        );
        return;
    }

    // Store selected file
    selectedFile = file;

    // Show file info bar
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    fileInfo.style.display = 'flex';

    // Enable parse button
    parseBtn.disabled = false;
}

function clearFile() {
    /** Clears the selected file and resets UI. */
    selectedFile = null;
    fileInput.value = '';
    fileInfo.style.display = 'none';
    parseBtn.disabled = true;
}


// ── Event Listeners for File Selection ────────────────────────

// Click on browse button → open file picker
dropZone.addEventListener('click', () => fileInput.click());

// File picked from file picker
fileInput.addEventListener('change', (e) => {
    if (e.target.files[0]) {
        handleFileSelect(e.target.files[0]);
    }
});

// Remove file button
removeFile.addEventListener('click', (e) => {
    e.stopPropagation(); // Prevent drop zone click
    clearFile();
});

// Drag and drop events
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault(); // Required to allow drop
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    handleFileSelect(file);
});


// ── Section Visibility Helpers ─────────────────────────────────

function showSection(sectionId) {
    /**
     * Shows one section and hides all others.
     * Sections: 'upload', 'loading', 'error', 'results'
     */
    uploadSection.style.display = 'none';
    loadingSection.style.display = 'none';
    errorSection.style.display = 'none';
    resultsSection.style.display = 'none';

    if (sectionId === 'upload') uploadSection.style.display = 'block';
    if (sectionId === 'loading') loadingSection.style.display = 'block';
    if (sectionId === 'error') errorSection.style.display = 'block';
    if (sectionId === 'results') resultsSection.style.display = 'block';
}

function resetToUpload() {
    /** Resets the entire UI back to the upload state. */
    clearFile();
    showSection('upload');
}


// ── Loading Steps Animation ────────────────────────────────────

function animateLoadingSteps() {
    /**
     * Animates the loading steps with delays
     * to show progress while waiting for the API.
     */
    const steps = ['step1', 'step2', 'step3', 'step4'];
    const messages = [
        'File uploaded successfully',
        'Extracting text from resume...',
        'AI is analyzing and parsing...',
        'Validating structured output...'
    ];

    // Step 1 is already done (file uploaded)
    document.getElementById('step1').className = 'step done';
    document.getElementById('step2').className = 'step active';

    // After 2 seconds, advance to step 3
    setTimeout(() => {
        document.getElementById('step2').className = 'step done';
        document.getElementById('step3').className = 'step active';
    }, 2000);

    // After 5 seconds, advance to step 4
    setTimeout(() => {
        document.getElementById('step3').className = 'step done';
        document.getElementById('step4').className = 'step active';
    }, 5000);
}


// ── Error Display ──────────────────────────────────────────────

function showError(errorCode, message, hint) {
    /**
     * Shows the error section with the given details.
     */
    document.getElementById('errorCode').textContent =
        errorCode || 'Error';
    document.getElementById('errorMessage').textContent =
        message || 'Something went wrong.';
    document.getElementById('errorHint').textContent =
        hint || '';

    showSection('error');
}


// ── Results Display ────────────────────────────────────────────

function displayResults(apiResponse) {
    /**
     * Takes the full API response and renders it in the UI.
     * Fills metadata bar and both the formatted and JSON views.
     */

    const metadata = apiResponse.metadata || {};
    const data = apiResponse.data || {};

    // ── Fill metadata bar ──────────────────────────────────────
    document.getElementById('metaTime').textContent =
        `${metadata.processing_time_seconds}s`;
    document.getElementById('metaWords').textContent =
        (metadata.word_count || 0).toLocaleString();
    document.getElementById('metaSize').textContent =
        `${metadata.file_size_mb} MB`;
    document.getElementById('metaModel').textContent =
        (metadata.model_used || '').split('-').slice(0, 3).join('-');

    // ── Fill JSON view ─────────────────────────────────────────
    document.getElementById('jsonOutput').textContent =
        JSON.stringify(data, null, 2);

    // ── Fill formatted view ────────────────────────────────────
    const grid = document.getElementById('resultGrid');
    grid.innerHTML = '';

    // Helper: create a result card
    function makeCard(title, content, fullWidth = false) {
        const card = document.createElement('div');
        card.className = 'result-card' + (fullWidth ? ' full-width' : '');
        card.innerHTML = `<h3>${title}</h3>
                          <div class="result-value">${content}</div>`;
        grid.appendChild(card);
    }

    // Helper: render a value or show "Not found"
    function val(v) {
        if (v === null || v === undefined || v === '') {
            return '<span class="null-value">Not found</span>';
        }
        return `<span>${v}</span>`;
    }

    // ── Personal Info Card ─────────────────────────────────────
    makeCard('👤 Personal Information', `
        <table style="width:100%; border-collapse:collapse; font-size:0.9rem;">
            <tr><td style="padding:4px 8px; color:#999; width:40%">
                Name</td>
                <td>${val(data.full_name)}</td></tr>
            <tr><td style="padding:4px 8px; color:#999">
                Email</td>
                <td>${val(data.email)}</td></tr>
            <tr><td style="padding:4px 8px; color:#999">
                Phone</td>
                <td>${val(data.phone)}</td></tr>
            <tr><td style="padding:4px 8px; color:#999">
                Location</td>
                <td>${val(data.location)}</td></tr>
            <tr><td style="padding:4px 8px; color:#999">
                LinkedIn</td>
                <td>${val(data.linkedin)}</td></tr>
            <tr><td style="padding:4px 8px; color:#999">
                GitHub</td>
                <td>${val(data.github)}</td></tr>
            <tr><td style="padding:4px 8px; color:#999">
                Portfolio</td>
                <td>${val(data.portfolio)}</td></tr>
        </table>
    `);

    // ── Summary Card ───────────────────────────────────────────
    if (data.summary) {
        makeCard('📝 Summary',
            `<p style="color:#555; line-height:1.6; font-size:0.9rem;">
                ${data.summary}
             </p>`
        );
    }

    // ── Skills Card ────────────────────────────────────────────
    const skills = data.skills || [];
    if (skills.length > 0) {
        const skillTags = skills.map(s =>
            `<span class="tag">${s}</span>`
        ).join('');
        makeCard('🛠️ Skills', skillTags);
    }

    // ── Education Card ─────────────────────────────────────────
    const education = data.education || [];
    if (education.length > 0) {
        const eduHTML = education.map(edu => `
            <div class="entry-block">
                <div class="entry-title">
                    ${edu.degree || 'Unknown Degree'}
                </div>
                <div class="entry-subtitle">
                    🏫 ${edu.institution || 'Unknown Institution'}
                </div>
                <div class="entry-date">
                    📅 ${edu.start_date || '?'} – ${edu.end_date || '?'}
                    ${edu.grade ? `· 🏆 ${edu.grade}` : ''}
                </div>
            </div>
        `).join('');
        makeCard('🎓 Education', eduHTML);
    }

    // ── Experience Card ────────────────────────────────────────
    const experience = data.experience || [];
    if (experience.length > 0) {
        const expHTML = experience.map(exp => `
            <div class="entry-block">
                <div class="entry-title">
                    ${exp.job_title || 'Unknown Role'}
                </div>
                <div class="entry-subtitle">
                    🏢 ${exp.company || 'Unknown Company'}
                    ${exp.location ? `· 📍 ${exp.location}` : ''}
                </div>
                <div class="entry-date">
                    📅 ${exp.start_date || '?'} – ${exp.end_date || '?'}
                </div>
                ${exp.description ?
                    `<div class="entry-desc">${exp.description}</div>`
                    : ''
                }
            </div>
        `).join('');
        makeCard('💼 Experience', expHTML, true);
    }

    // ── Projects Card ──────────────────────────────────────────
    const projects = data.projects || [];
    if (projects.length > 0) {
        const projHTML = projects.map(proj => `
            <div class="entry-block">
                <div class="entry-title">
                    🚀 ${proj.name || 'Unnamed Project'}
                </div>
                ${proj.description ?
                    `<div class="entry-desc">${proj.description}</div>`
                    : ''
                }
                ${proj.technologies && proj.technologies.length > 0 ?
                    `<div style="margin-top:8px">
                        ${proj.technologies.map(t =>
                            `<span class="tag">${t}</span>`
                        ).join('')}
                     </div>`
                    : ''
                }
            </div>
        `).join('');
        makeCard('🚀 Projects', projHTML, true);
    }

    // ── Certifications Card ────────────────────────────────────
    const certs = data.certifications || [];
    if (certs.length > 0) {
        const certHTML = certs.map(c =>
            `<span class="tag">🏅 ${c}</span>`
        ).join('');
        makeCard('📜 Certifications', certHTML);
    }

    // ── Languages Card ─────────────────────────────────────────
    const languages = data.languages || [];
    if (languages.length > 0) {
        const langHTML = languages.map(l =>
            `<span class="tag">🌍 ${l}</span>`
        ).join('');
        makeCard('🌍 Languages', langHTML);
    }

    // ── Show results section ───────────────────────────────────
    showSection('results');
}


// ── Tab Switching ──────────────────────────────────────────────

document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        // Remove active from all tabs and content
        document.querySelectorAll('.tab').forEach(t =>
            t.classList.remove('active')
        );
        document.querySelectorAll('.tab-content').forEach(c =>
            c.classList.remove('active')
        );

        // Add active to clicked tab
        tab.classList.add('active');

        // Show matching content
        const tabName = tab.getAttribute('data-tab');
        document.getElementById(`tab-${tabName}`)
                .classList.add('active');
    });
});


// ── Copy JSON Button ───────────────────────────────────────────

copyJsonBtn.addEventListener('click', () => {
    const jsonText = document.getElementById('jsonOutput').textContent;
    navigator.clipboard.writeText(jsonText).then(() => {
        copyJsonBtn.textContent = '✅ Copied!';
        setTimeout(() => {
            copyJsonBtn.textContent = '📋 Copy JSON';
        }, 2000);
    });
});


// ── Try Again / Parse Another ──────────────────────────────────

tryAgainBtn.addEventListener('click', resetToUpload);
parseAnotherBtn.addEventListener('click', resetToUpload);


// ── Main Parse Function ────────────────────────────────────────

parseBtn.addEventListener('click', async () => {
    /**
     * This is the main function that runs when user clicks Parse.
     *
     * Steps:
     * 1. Show loading screen
     * 2. Start loading animation
     * 3. Build form data with the file
     * 4. Send POST request to our API
     * 5. Handle success or error response
     */

    if (!selectedFile) return;

    // ── Step 1: Show loading screen ────────────────────────────
    showSection('loading');
    animateLoadingSteps();

    // ── Step 2: Build form data ────────────────────────────────
    // FormData is how we send files via JavaScript fetch
    const formData = new FormData();
    formData.append('file', selectedFile);

    // ── Step 3: Send request to API ────────────────────────────
    try {
        const response = await fetch('/api/v1/parse-resume', {
            method: 'POST',
            body: formData
            // Note: Do NOT set Content-Type header manually
            // The browser sets it automatically with the boundary
        });

        // Parse the JSON response
        const result = await response.json();

        // ── Step 4: Handle response ────────────────────────────
        if (response.ok && result.status === 'success') {
            // Success — show results
            displayResults(result);

        } else {
            // API returned an error response
            showError(
                result.error_code || 'API_ERROR',
                result.message || 'Parsing failed.',
                result.hint || null
            );
        }

    } catch (error) {
        // Network error — cannot reach API at all
        showError(
            'NETWORK_ERROR',
            'Cannot connect to the server.',
            'Make sure the FastAPI server is running.'
        );
    }
});