/**
 * FractureAI — Live Camera Scanner
 * ===================================
 * Handles webcam access, frame capture, and
 * sends captured images to the AI analysis API.
 */

let cameraStream = null;

/**
 * Start the webcam camera feed.
 * Requests camera permission and displays the video feed.
 */
async function startCamera() {
    const video = document.getElementById('camera-feed');
    const cameraOff = document.getElementById('camera-off');
    const captureBtn = document.getElementById('camera-capture-btn');
    const startBtn = document.getElementById('camera-start-btn');
    const overlay = document.getElementById('camera-scan-overlay');

    if (!video) return;

    try {
        // Request camera access
        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: 'environment', // Prefer back camera on mobile
                width: { ideal: 1280 },
                height: { ideal: 720 },
            }
        });

        cameraStream = stream;
        video.srcObject = stream;
        video.classList.remove('hidden');
        video.play();

        // Update UI
        if (cameraOff) cameraOff.classList.add('hidden');
        if (overlay) overlay.classList.remove('hidden');
        if (captureBtn) captureBtn.disabled = false;

        // Change start button to stop
        if (startBtn) {
            startBtn.innerHTML = '<i class="fa-solid fa-stop mr-2"></i>Stop Camera';
            startBtn.onclick = stopCamera;
            startBtn.classList.remove('text-neon-green', 'border-neon-green/30', 'hover:bg-neon-green/10');
            startBtn.classList.add('text-red-400', 'border-red-400/30', 'hover:bg-red-400/10');
        }

    } catch (err) {
        console.error('Camera access error:', err);
        alert('Could not access camera. Please ensure camera permissions are granted.');
    }
}

/**
 * Stop the webcam feed.
 */
function stopCamera() {
    const video = document.getElementById('camera-feed');
    const cameraOff = document.getElementById('camera-off');
    const captureBtn = document.getElementById('camera-capture-btn');
    const startBtn = document.getElementById('camera-start-btn');
    const overlay = document.getElementById('camera-scan-overlay');

    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
        cameraStream = null;
    }

    if (video) {
        video.srcObject = null;
        video.classList.add('hidden');
    }
    if (cameraOff) cameraOff.classList.remove('hidden');
    if (overlay) overlay.classList.add('hidden');
    if (captureBtn) captureBtn.disabled = true;

    // Restore start button
    if (startBtn) {
        startBtn.innerHTML = '<i class="fa-solid fa-play mr-2"></i>Start Camera';
        startBtn.onclick = startCamera;
        startBtn.classList.remove('text-red-400', 'border-red-400/30', 'hover:bg-red-400/10');
        startBtn.classList.add('text-neon-green', 'border-neon-green/30', 'hover:bg-neon-green/10');
    }
}

/**
 * Capture a frame from the camera and send it to the API for analysis.
 */
async function captureAndAnalyze() {
    const video = document.getElementById('camera-feed');
    const canvas = document.getElementById('camera-canvas');
    const resultDiv = document.getElementById('camera-result');
    const resultContent = document.getElementById('camera-result-content');
    const captureBtn = document.getElementById('camera-capture-btn');

    if (!video || !canvas || !cameraStream) {
        alert('Camera is not active. Please start the camera first.');
        return;
    }

    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw the current video frame onto the canvas
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);

    // Convert canvas to base64 JPEG
    const imageData = canvas.toDataURL('image/jpeg', 0.9);

    // Get selected body part
    const bodyPartSelect = document.getElementById('body-part-select');
    const bodyPart = bodyPartSelect ? bodyPartSelect.value : 'Unknown';

    // Show loading state
    if (captureBtn) {
        captureBtn.disabled = true;
        captureBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-2"></i>Analyzing...';
    }

    try {
        // Send to API
        const response = await fetch('/api/analyze-camera', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image: imageData,
                body_part: bodyPart,
            }),
        });

        const data = await response.json();

        if (data.success) {
            // Display results
            showCameraResult(data);
        } else {
            resultContent.innerHTML = `<p class="text-red-400 text-sm">${data.error || 'Analysis failed'}</p>`;
        }

        resultDiv.classList.remove('hidden');

    } catch (err) {
        console.error('Camera analysis error:', err);
        resultContent.innerHTML = '<p class="text-red-400 text-sm">Error connecting to server.</p>';
        resultDiv.classList.remove('hidden');
    }

    // Restore button
    if (captureBtn) {
        captureBtn.disabled = false;
        captureBtn.innerHTML = '<i class="fa-solid fa-camera mr-2"></i>Capture & Analyze';
    }
}


/**
 * Display camera analysis results in the result panel.
 * 
 * @param {Object} data - API response data
 */
function showCameraResult(data) {
    const content = document.getElementById('camera-result-content');
    if (!content) return;

    const statusColor = data.fracture_detected ? 'text-red-400' : 'text-emerald-400';
    const statusIcon = data.fracture_detected ? 'fa-triangle-exclamation' : 'fa-circle-check';
    const statusText = data.fracture_detected ? 'FRACTURE DETECTED' : 'NO FRACTURE DETECTED';

    let html = `
        <div class="flex items-center gap-2 mb-3">
            <i class="fa-solid ${statusIcon} ${statusColor}"></i>
            <span class="font-bold ${statusColor}">${statusText}</span>
        </div>
        <div class="grid grid-cols-2 gap-3 text-sm">
            <div>
                <span class="text-gray-500">Confidence:</span>
                <span class="text-cyan-400 font-mono ml-1">${data.confidence}%</span>
            </div>
            <div>
                <span class="text-gray-500">Severity:</span>
                <span class="ml-1 font-bold ${
                    data.severity === 'High' ? 'text-red-400' :
                    data.severity === 'Medium' ? 'text-amber-400' :
                    data.severity === 'Low' ? 'text-green-400' : 'text-gray-400'
                }">${data.severity}</span>
            </div>
            <div class="col-span-2">
                <span class="text-gray-500">Type:</span>
                <span class="text-gray-300 ml-1">${data.fracture_type}</span>
            </div>
        </div>
    `;

    // Add link to full result
    if (data.scan_id) {
        html += `
            <a href="/result/${data.scan_id}" class="mt-4 inline-flex items-center gap-2 text-cyan-400 hover:text-cyan-300 text-sm font-medium">
                <i class="fa-solid fa-arrow-right"></i> View Full Results
            </a>
        `;
    }

    content.innerHTML = html;
}
