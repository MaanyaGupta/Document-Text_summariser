/**
 * Document Summarizer - Frontend Application
 */

// State
const state = {
    file: null,
    length: 'medium',
    currentResult: null
};

// DOM Elements
const elements = {
    // Tabs
    tabs: document.querySelectorAll('.tab'),
    uploadTab: document.getElementById('uploadTab'),
    pasteTab: document.getElementById('pasteTab'),

    // File upload
    dropzone: document.getElementById('dropzone'),
    fileInput: document.getElementById('fileInput'),
    fileInfo: document.getElementById('fileInfo'),
    fileName: document.getElementById('fileName'),
    clearFile: document.getElementById('clearFile'),

    // Text input
    textInput: document.getElementById('textInput'),

    // Options
    lengthToggles: document.querySelectorAll('[data-length]'),
    saveCheckbox: document.getElementById('saveCheckbox'),

    // Actions
    summarizeBtn: document.getElementById('summarizeBtn'),

    // Results
    resultsSection: document.getElementById('resultsSection'),
    resultsMeta: document.getElementById('resultsMeta'),
    summaryContent: document.getElementById('summaryContent'),
    keyPointsList: document.getElementById('keyPointsList'),
    copySummary: document.getElementById('copySummary'),
    copyKeyPoints: document.getElementById('copyKeyPoints'),
    exportTxt: document.getElementById('exportTxt'),
    exportJson: document.getElementById('exportJson'),

    // Sidebar
    sidebar: document.getElementById('sidebar'),
    toggleSidebar: document.getElementById('toggleSidebar'),
    refreshSaved: document.getElementById('refreshSaved'),
    savedList: document.getElementById('savedList'),

    // Loading & Toast
    loadingOverlay: document.getElementById('loadingOverlay'),
    toast: document.getElementById('toast')
};

// Initialize
function init() {
    setupEventListeners();
    loadSavedSummaries();
}

// Event Listeners
function setupEventListeners() {
    // Tabs
    elements.tabs.forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });

    // File upload
    elements.dropzone.addEventListener('click', () => elements.fileInput.click());
    elements.fileInput.addEventListener('change', handleFileSelect);
    elements.dropzone.addEventListener('dragover', handleDragOver);
    elements.dropzone.addEventListener('dragleave', handleDragLeave);
    elements.dropzone.addEventListener('drop', handleDrop);
    elements.clearFile.addEventListener('click', clearFile);

    // Length toggles
    elements.lengthToggles.forEach(toggle => {
        toggle.addEventListener('click', () => setLength(toggle.dataset.length));
    });

    // Summarize button
    elements.summarizeBtn.addEventListener('click', handleSummarize);

    // Copy buttons
    elements.copySummary.addEventListener('click', () => copyToClipboard(state.currentResult?.summary));
    elements.copyKeyPoints.addEventListener('click', () => {
        const points = state.currentResult?.key_points?.join('\n• ') || '';
        copyToClipboard('• ' + points);
    });

    // Export buttons
    elements.exportTxt.addEventListener('click', () => exportResult('txt'));
    elements.exportJson.addEventListener('click', () => exportResult('json'));

    // Sidebar
    elements.toggleSidebar.addEventListener('click', toggleSidebar);
    elements.refreshSaved.addEventListener('click', loadSavedSummaries);
}

// Tab switching
function switchTab(tabName) {
    elements.tabs.forEach(t => t.classList.toggle('active', t.dataset.tab === tabName));
    elements.uploadTab.classList.toggle('active', tabName === 'upload');
    elements.pasteTab.classList.toggle('active', tabName === 'paste');
}

// File handling
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) setFile(file);
}

function handleDragOver(e) {
    e.preventDefault();
    elements.dropzone.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    elements.dropzone.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    elements.dropzone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file) setFile(file);
}

function setFile(file) {
    const validTypes = ['.pdf', '.docx', '.txt', '.md', '.text'];
    const ext = '.' + file.name.split('.').pop().toLowerCase();

    if (!validTypes.includes(ext)) {
        showToast('Unsupported file type. Use PDF, DOCX, or TXT.', 'error');
        return;
    }

    state.file = file;
    elements.fileName.textContent = file.name;
    elements.fileInfo.hidden = false;
    elements.dropzone.style.display = 'none';
}

function clearFile() {
    state.file = null;
    elements.fileInput.value = '';
    elements.fileInfo.hidden = true;
    elements.dropzone.style.display = 'block';
}

// Length
function setLength(length) {
    state.length = length;
    elements.lengthToggles.forEach(t => t.classList.toggle('active', t.dataset.length === length));
}


// Summarize
async function handleSummarize() {
    const isUploadTab = elements.uploadTab.classList.contains('active');

    // Validate input
    if (isUploadTab && !state.file) {
        showToast('Please upload a file first', 'error');
        return;
    }

    if (!isUploadTab && !elements.textInput.value.trim()) {
        showToast('Please enter some text', 'error');
        return;
    }

    // Build request
    const params = new URLSearchParams({
        length: state.length,
        save: elements.saveCheckbox.checked ? 'true' : 'false'
    });

    showLoading(true);

    try {
        let response;

        if (isUploadTab) {
            // File upload
            const formData = new FormData();
            formData.append('file', state.file);

            response = await fetch(`/api/summarize?${params}`, {
                method: 'POST',
                body: formData
            });
        } else {
            // Text input
            response = await fetch(`/api/summarize?${params}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: elements.textInput.value,
                    filename: 'pasted_text'
                })
            });
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Summarization failed');
        }

        displayResults(data);
        showToast('Summary generated successfully!', 'success');

        if (data.saved_id) {
            loadSavedSummaries();
        }

    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// Display results
function displayResults(data) {
    state.currentResult = data;

    // Meta info
    elements.resultsMeta.textContent =
        `${data.mode.toUpperCase()} • ${data.length} • ${data.original_length.toLocaleString()} → ${data.summary_length.toLocaleString()} chars`;

    // Summary
    elements.summaryContent.textContent = data.summary;

    // Key points
    elements.keyPointsList.innerHTML = data.key_points
        .map(point => `<li>${escapeHtml(point)}</li>`)
        .join('');

    // Show results
    elements.resultsSection.hidden = false;
    elements.resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Export
function exportResult(format) {
    if (!state.currentResult) return;

    let content, filename, type;

    if (format === 'json') {
        content = JSON.stringify(state.currentResult, null, 2);
        filename = 'summary.json';
        type = 'application/json';
    } else {
        content = `Document: ${state.currentResult.filename}\n`;
        content += `Mode: ${state.currentResult.mode} | Length: ${state.currentResult.length}\n`;
        content += '\n' + '='.repeat(50) + '\n';
        content += 'SUMMARY\n';
        content += '='.repeat(50) + '\n';
        content += state.currentResult.summary + '\n\n';
        content += '='.repeat(50) + '\n';
        content += 'KEY POINTS\n';
        content += '='.repeat(50) + '\n';
        state.currentResult.key_points.forEach((p, i) => {
            content += `${i + 1}. ${p}\n`;
        });
        filename = 'summary.txt';
        type = 'text/plain';
    }

    downloadFile(content, filename, type);
}

// Saved summaries
async function loadSavedSummaries() {
    try {
        const response = await fetch('/api/summaries');
        const data = await response.json();

        if (data.summaries && data.summaries.length > 0) {
            elements.savedList.innerHTML = data.summaries.map(s => `
                <div class="saved-item" data-id="${s.id}">
                    <div class="saved-item-header">
                        <span class="saved-item-title">${escapeHtml(s.filename)}</span>
                        <button class="saved-item-delete" data-id="${s.id}">🗑️</button>
                    </div>
                    <div class="saved-item-meta">${s.mode} • ${s.length} • ${formatDate(s.created_at)}</div>
                    <div class="saved-item-preview">${escapeHtml(s.summary_preview || '')}</div>
                </div>
            `).join('');

            // Add click handlers
            elements.savedList.querySelectorAll('.saved-item').forEach(item => {
                item.addEventListener('click', (e) => {
                    if (!e.target.classList.contains('saved-item-delete')) {
                        loadSavedSummary(item.dataset.id);
                    }
                });
            });

            elements.savedList.querySelectorAll('.saved-item-delete').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    deleteSavedSummary(btn.dataset.id);
                });
            });
        } else {
            elements.savedList.innerHTML = '<div class="empty-state"><span>No saved summaries</span></div>';
        }
    } catch (error) {
        console.error('Failed to load saved summaries:', error);
    }
}

async function loadSavedSummary(id) {
    try {
        const response = await fetch(`/api/summaries/${id}`);
        const data = await response.json();

        if (response.ok) {
            displayResults(data);
        }
    } catch (error) {
        showToast('Failed to load summary', 'error');
    }
}

async function deleteSavedSummary(id) {
    if (!confirm('Delete this summary?')) return;

    try {
        const response = await fetch(`/api/summaries/${id}`, { method: 'DELETE' });

        if (response.ok) {
            showToast('Summary deleted', 'success');
            loadSavedSummaries();
        }
    } catch (error) {
        showToast('Failed to delete summary', 'error');
    }
}

// Sidebar
function toggleSidebar() {
    elements.sidebar.classList.toggle('hidden');
    elements.sidebar.classList.toggle('visible');
}

// Utilities
function showLoading(show) {
    elements.loadingOverlay.classList.toggle('active', show);
}

function showToast(message, type = 'info') {
    elements.toast.textContent = message;
    elements.toast.className = `toast show ${type}`;

    setTimeout(() => {
        elements.toast.classList.remove('show');
    }, 3000);
}

function copyToClipboard(text) {
    if (!text) return;

    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(() => {
        showToast('Failed to copy', 'error');
    });
}

function downloadFile(content, filename, type) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', init);
