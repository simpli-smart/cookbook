/**
 * Qwen3-TTS Interactive Demo - Frontend JavaScript
 */

// DOM Elements
const textInput = document.getElementById('text-input');
const charCount = document.getElementById('char-count');
const clearBtn = document.getElementById('clear-btn');
const speakerSelect = document.getElementById('speaker-select');
const speakerDescription = document.getElementById('speaker-description');
const languageSelect = document.getElementById('language-select');
const instructInput = document.getElementById('instruct-input');
const leadingSilence = document.getElementById('leading-silence');
const generateBtn = document.getElementById('generate-btn');
const generateIcon = document.getElementById('generate-icon');
const generateText = document.getElementById('generate-text');
const playerSection = document.getElementById('player-section');
const audioPlayer = document.getElementById('audio-player');
const audioMetrics = document.getElementById('audio-metrics');
const downloadBtn = document.getElementById('download-btn');
const waveform = document.getElementById('waveform');
const errorDisplay = document.getElementById('error-display');
const errorMessage = document.getElementById('error-message');
const historyList = document.getElementById('history-list');
const clearHistoryBtn = document.getElementById('clear-history');

// State
let isGenerating = false;
let audioBlob = null;
let audioUrl = null;
let apiHealthy = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    init();
});

async function init() {
    updateCharCount();
    updateSpeakerDescription();
    loadHistory();
    setupEventListeners();
    await checkApiHealth();
}

// Check API health on startup
async function checkApiHealth() {
    const configStatus = document.getElementById('config-status');
    const generateBtn = document.getElementById('generate-btn');

    // Show checking status
    configStatus.innerHTML = `
        <span class="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></span>
        <span class="text-yellow-400">Checking API...</span>
    `;

    try {
        const response = await fetch('/api/health');
        const data = await response.json();

        if (response.ok && data.api_reachable) {
            apiHealthy = true;
            configStatus.innerHTML = `
                <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                <span class="text-green-400">API Ready</span>
            `;
            generateBtn.disabled = false;
        } else {
            apiHealthy = false;
            configStatus.innerHTML = `
                <span class="w-2 h-2 bg-red-500 rounded-full"></span>
                <span class="text-red-400">API Unavailable</span>
            `;
            generateBtn.disabled = true;
            showError(data.message || 'TTS API is not reachable. Please check your configuration.');
        }
    } catch (error) {
        apiHealthy = false;
        configStatus.innerHTML = `
            <span class="w-2 h-2 bg-red-500 rounded-full"></span>
            <span class="text-red-400">API Check Failed</span>
        `;
        generateBtn.disabled = true;
        showError('Failed to check API health: ' + error.message);
    }
}

// Event Listeners
function setupEventListeners() {
    // Text input
    textInput.addEventListener('input', updateCharCount);
    clearBtn.addEventListener('click', () => {
        textInput.value = '';
        updateCharCount();
        textInput.focus();
    });

    // Speaker selection
    speakerSelect.addEventListener('change', updateSpeakerDescription);

    // Preset buttons
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            textInput.value = btn.dataset.text;
            updateCharCount();
        });
    });

    // Instruction presets
    document.querySelectorAll('.instruct-preset').forEach(btn => {
        btn.addEventListener('click', () => {
            instructInput.value = btn.dataset.value;
        });
    });

    // Generate button
    generateBtn.addEventListener('click', generateSpeech);

    // Audio player events
    audioPlayer.addEventListener('play', () => {
        waveform.classList.remove('hidden');
    });
    audioPlayer.addEventListener('pause', () => {
        waveform.classList.add('hidden');
    });
    audioPlayer.addEventListener('ended', () => {
        waveform.classList.add('hidden');
    });

    // Clear history
    clearHistoryBtn.addEventListener('click', clearHistory);
}

// Update character count
function updateCharCount() {
    const count = textInput.value.length;
    charCount.textContent = `${count} character${count !== 1 ? 's' : ''}`;
}

// Update speaker description
function updateSpeakerDescription() {
    const selected = speakerSelect.options[speakerSelect.selectedIndex];
    const description = selected.text.split(' - ')[1];
    speakerDescription.textContent = description || '';
}

// Show error
function showError(message) {
    errorMessage.textContent = message;
    errorDisplay.classList.remove('hidden');
    setTimeout(() => {
        errorDisplay.classList.add('hidden');
    }, 5000);
}

// Hide error
function hideError() {
    errorDisplay.classList.add('hidden');
}

// Generate speech
async function generateSpeech() {
    if (isGenerating) return;

    if (!apiHealthy) {
        showError('TTS API is not available. Please wait for the API health check to complete or refresh the page.');
        return;
    }

    const text = textInput.value.trim();
    if (!text) {
        showError('Please enter text to convert to speech');
        return;
    }

    hideError();
    isGenerating = true;
    updateGenerateButton(true);

    try {
        const payload = {
            text: text,
            language: languageSelect.value,
            speaker: speakerSelect.value,
            instruct: instructInput.value.trim(),
            leading_silence: leadingSilence.checked,
        };

        console.log('[DEBUG] Frontend payload:', payload);

        const response = await fetch('/api/tts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || `HTTP error! status: ${response.status}`);
        }

        // Get the audio blob
        audioBlob = await response.blob();
        audioUrl = URL.createObjectURL(audioBlob);

        // Update player
        audioPlayer.src = audioUrl;
        playerSection.classList.remove('hidden');

        // Update download button
        const filename = response.headers.get('content-disposition')?.match(/filename="?([^"]+)"?/)?.[1] || 'generated.wav';
        downloadBtn.href = audioUrl;
        downloadBtn.download = filename;

        // Get metrics from history
        await loadHistory();

        // Auto-play
        audioPlayer.play();

    } catch (error) {
        console.error('Generation error:', error);
        showError(error.message || 'Failed to generate speech. Please try again.');
    } finally {
        isGenerating = false;
        updateGenerateButton(false);
    }
}

// Update generate button state
function updateGenerateButton(loading) {
    if (loading) {
        generateBtn.disabled = true;
        generateText.textContent = 'Generating...';
        generateIcon.innerHTML = `
            <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
        `;
    } else {
        generateBtn.disabled = false;
        generateText.textContent = 'Generate Speech';
        generateIcon.innerHTML = `
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"></path>
            </svg>
        `;
    }
}

// Load history
async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        const history = await response.json();
        renderHistory(history);
    } catch (error) {
        console.error('Failed to load history:', error);
    }
}

// Render history
function renderHistory(history) {
    if (history.length === 0) {
        historyList.innerHTML = '<p class="text-slate-500 text-sm text-center py-8">No generations yet</p>';
        return;
    }

    historyList.innerHTML = history.map((item, index) => `
        <div class="bg-slate-800/50 rounded-lg p-3 hover:bg-slate-800 transition-colors cursor-pointer group" data-filename="${item.filename}">
            <div class="flex items-start justify-between">
                <div class="flex-1 min-w-0">
                    <p class="text-sm text-slate-300 truncate">${escapeHtml(item.text)}</p>
                    <div class="flex items-center space-x-2 mt-1 text-xs text-slate-500">
                        <span class="px-1.5 py-0.5 bg-slate-700 rounded">${item.speaker}</span>
                        <span class="px-1.5 py-0.5 bg-slate-700 rounded">${item.language}</span>
                        <span>${formatDuration(item.duration)}</span>
                    </div>
                </div>
                <button class="play-history-btn ml-2 p-1.5 rounded hover:bg-violet-600/30 text-slate-400 hover:text-violet-400 transition-colors" data-filename="${item.filename}" data-index="${index}">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                </button>
            </div>
        </div>
    `).join('');

    // Add click handlers for history items
    document.querySelectorAll('.play-history-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const filename = btn.dataset.filename;
            playHistoryItem(filename, btn.dataset.index);
        });
    });

    // Update latest metrics if available
    if (history.length > 0) {
        const latest = history[0];
        audioMetrics.textContent = `Duration: ${formatDuration(latest.duration)} | TTFC: ${latest.ttfc_ms?.toFixed(0) || '--'}ms`;
    }
}

// Play history item
async function playHistoryItem(filename, index) {
    try {
        const response = await fetch(`/api/outputs/${filename}`);
        if (!response.ok) throw new Error('Failed to load audio');

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        audioPlayer.src = url;
        playerSection.classList.remove('hidden');
        downloadBtn.href = url;
        downloadBtn.download = filename;

        // Highlight active item
        document.querySelectorAll('#history-list > div').forEach((div, i) => {
            if (i.toString() === index) {
                div.classList.add('ring-1', 'ring-violet-500');
            } else {
                div.classList.remove('ring-1', 'ring-violet-500');
            }
        });

        await audioPlayer.play();
    } catch (error) {
        console.error('Failed to play history item:', error);
        showError('Failed to load audio from history');
    }
}

// Clear history
async function clearHistory() {
    try {
        // Clear UI first
        historyList.innerHTML = '<p class="text-slate-500 text-sm text-center py-8">No generations yet</p>';

        // Clear on server
        await fetch('/api/history', { method: 'DELETE' });
    } catch (error) {
        console.error('Failed to clear history:', error);
    }
}

// Utility: Format duration
function formatDuration(seconds) {
    if (!seconds || isNaN(seconds)) return '--:--';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Utility: Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Enter to generate
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        generateSpeech();
    }
});
