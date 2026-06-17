/**
 * FractureAI — Voice Command System
 * ====================================
 * Uses the Web Speech API (SpeechRecognition) for
 * hands-free navigation via voice commands.
 */

let recognition = null;
let isListening = false;

/**
 * Start listening for voice commands.
 * Opens the voice overlay and begins speech recognition.
 */
function startVoiceCommand() {
    // Check browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        alert('Voice commands are not supported in this browser. Please use Chrome or Edge.');
        return;
    }

    const overlay = document.getElementById('voice-overlay');
    const voiceText = document.getElementById('voice-text');

    // Show overlay
    if (overlay) {
        overlay.classList.remove('hidden');
        overlay.classList.add('flex');
    }

    // Initialize speech recognition
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;

    // Set language based on current i18n setting
    const currentLang = localStorage.getItem('fractureai-lang') || 'en';
    recognition.lang = currentLang === 'hi' ? 'hi-IN' : 'en-US';

    isListening = true;

    // ── Handle Results ──
    recognition.onresult = async (event) => {
        const transcript = event.results[0][0].transcript;

        // Update the displayed text
        if (voiceText) {
            voiceText.textContent = `"${transcript}"`;
        }

        // Only process final result
        if (event.results[0].isFinal) {
            // Send command to backend API
            try {
                const response = await fetch('/api/voice-command', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: transcript }),
                });

                const data = await response.json();

                if (data.success) {
                    // show the recognized message
                    if (voiceText) {
                        voiceText.textContent = data.message || 'Command recognized!';
                    }

                    // Execute action after a brief delay
                    setTimeout(() => {
                        stopVoiceCommand();

                        if (data.action === 'navigate' && data.url) {
                            window.location.href = data.url;
                        } else if (data.action === 'open_camera') {
                            startCamera();
                        } else if (data.action === 'show_help') {
                            alert(data.message);
                        }
                    }, 1000);
                }

            } catch (err) {
                console.error('Voice command error:', err);
                if (voiceText) voiceText.textContent = 'Error processing command.';
                setTimeout(() => stopVoiceCommand(), 2000);
            }
        }
    };

    // ── Handle Errors ──
    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        if (voiceText) {
            if (event.error === 'no-speech') {
                voiceText.textContent = 'No speech detected. Try again.';
            } else if (event.error === 'not-allowed') {
                voiceText.textContent = 'Microphone access denied.';
            } else {
                voiceText.textContent = `Error: ${event.error}`;
            }
        }
        setTimeout(() => stopVoiceCommand(), 2000);
    };

    // ── Handle End ──
    recognition.onend = () => {
        isListening = false;
    };

    // Start listening
    recognition.start();
}

/**
 * Stop voice recognition and close the overlay.
 */
function stopVoiceCommand() {
    if (recognition) {
        recognition.abort();
        recognition = null;
    }

    isListening = false;

    const overlay = document.getElementById('voice-overlay');
    if (overlay) {
        overlay.classList.add('hidden');
        overlay.classList.remove('flex');
    }

    // Reset the displayed text
    const voiceText = document.getElementById('voice-text');
    if (voiceText) {
        voiceText.textContent = 'Say a command...';
    }
}

// Global keyboard shortcut: Press "V" to activate voice command
document.addEventListener('keydown', (e) => {
    // Only trigger if not typing in an input/textarea
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    if (e.key === 'v' || e.key === 'V') {
        if (!isListening) {
            startVoiceCommand();
        }
    }
    if (e.key === 'Escape' && isListening) {
        stopVoiceCommand();
    }
});
