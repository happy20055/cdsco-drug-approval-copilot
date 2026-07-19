document.addEventListener("DOMContentLoaded", () => {
    setupDropzone("drop-zone-1", "file-info-1", "file1");
    setupDropzone("drop-zone-2", "file-info-2", "file2");
});

function setupDropzone(zoneId, infoId, inputId) {
    const zone = document.getElementById(zoneId);
    const info = document.getElementById(infoId);
    const input = document.getElementById(inputId);
    
    if (!zone || !info || !input) return;
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        zone.addEventListener(eventName, e => {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });
    
    ['dragenter', 'dragover'].forEach(eventName => {
        zone.addEventListener(eventName, () => zone.classList.add('dragover'), false);
    });
    ['dragleave', 'drop'].forEach(eventName => {
        zone.addEventListener(eventName, () => zone.classList.remove('dragover'), false);
    });
    
    zone.addEventListener('drop', e => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length) {
            input.files = files;
            updateFileInfo(files[0], info);
        }
    });
    
    input.addEventListener('change', () => {
        if (input.files.length) {
            updateFileInfo(input.files[0], info);
        }
    });
}

function updateFileInfo(file, infoElement) {
    const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
    infoElement.innerHTML = `
        <span class="file-info-name">📄 ${file.name}</span>
        <span class="file-info-size">${sizeMB} MB</span>
        <span class="file-info-reset" onclick="resetFile(event, '${infoElement.id}')">Remove File</span>
    `;
    infoElement.classList.add('active');
}

function resetFile(event, infoId) {
    event.stopPropagation();
    event.preventDefault();
    const info = document.getElementById(infoId);
    const inputId = infoId === 'file-info-1' ? 'file1' : 'file2';
    const input = document.getElementById(inputId);
    
    if (input) input.value = '';
    if (info) {
        info.classList.remove('active');
        info.innerHTML = '';
    }
}
window.resetFile = resetFile;

/* ==========================================================================
   Analysis Trigger & Render
   ========================================================================== */
async function processFiles() {
    const file1 = document.getElementById("file1").files[0];
    const file2 = document.getElementById("file2").files[0];

    if (!file1) {
        alert("Please select a primary document.");
        return;
    }

    const formData = new FormData();
    formData.append("file1", file1);
    if (file2) {
        formData.append("file2", file2);
    }

    // Loader display & simulation
    const loadingOverlay = document.getElementById("loading");
    const progressFill = document.getElementById("loader-progress");
    const subLabel = document.getElementById("loader-subtitle");
    
    loadingOverlay.style.display = "flex";
    progressFill.style.width = "0%";
    
    const loadingPhases = [
        "Reading document structure and text alignment...",
        "Running OCR engine on scanned visual pages...",
        "Filtering metadata and removing extraneous document headers...",
        "Applying entity regex and name-masking redaction vectors...",
        "Loading zero-shot classification pipelines...",
        "Evaluating semantic clinical completeness fields...",
        "Predicting document incident severity levels...",
        "Recursively compiling multi-page BART abstractive summaries...",
        "Calculating sentence-level duplicate embeddings...",
        "Assembling report and drafting ReportLab PDF document..."
    ];
    let currentPhaseIdx = 0;
    subLabel.textContent = loadingPhases[0];
    
    const phraseInterval = setInterval(() => {
        currentPhaseIdx = (currentPhaseIdx + 1) % loadingPhases.length;
        subLabel.textContent = loadingPhases[currentPhaseIdx];
    }, 2800);

    let progress = 0;
    const progressInterval = setInterval(() => {
        if (progress < 92) {
            progress += (92 - progress) * 0.08;
            progressFill.style.width = `${progress}%`;
        }
    }, 450);

    try {
        const response = await fetch("/process", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Server returned status ${response.status}`);
        }

        const data = await response.json();
        
        // Clean loader
        clearInterval(phraseInterval);
        clearInterval(progressInterval);
        progressFill.style.width = "100%";
        
        setTimeout(() => {
            loadingOverlay.style.display = "none";
            renderDashboard(data);
        }, 400);

    } catch (error) {
        clearInterval(phraseInterval);
        clearInterval(progressInterval);
        loadingOverlay.style.display = "none";
        
        document.getElementById("dynamic-panel").innerHTML = `
            <div class="welcome-container" style="color:var(--accent-rose);">
                <div class="welcome-icon" style="color:var(--accent-rose); border-color:rgba(244,63,94,0.2);">
                    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                </div>
                <h2>Execution Failure</h2>
                <p>An error occurred while compiling analysis results. Please ensure the backend is running and correct file formats are supplied.</p>
                <pre style="background:rgba(244,63,94,0.05); color:#fecdd3; border:1px solid rgba(244,63,94,0.1); padding:15px; border-radius:8px; text-align:left; font-size:12px; width:100%; max-width:600px;">${error.message}</pre>
            </div>
        `;
    }
}

function renderDashboard(data) {
    const classification = data.classification || { type: "General Document", confidence: 0 };
    const completeness = data.completeness || { present_fields: [], completeness_score: 0, severity: { severity: "not serious", confidence: 1 } };
    const metrics = data.summary_metrics || { reduction_percent: 0, compression_ratio: 1 };
    
    const panel = document.getElementById("dynamic-panel");
    panel.innerHTML = `
        <div class="results-dashboard">
            <!-- Header Row -->
            <div class="dashboard-header-row">
                <h2>Analysis Completed</h2>
                <div style="display:flex; gap:10px; align-items:center;">
                    <span class="status-label" style="color:var(--text-secondary); text-transform:uppercase; font-size:11px; letter-spacing:0.5px;">Doc Type:</span>
                    <span class="status-label" style="color:var(--accent-cyan); background:rgba(0,242,254,0.08); border:1px solid rgba(0,242,254,0.2); padding:4px 10px; border-radius:12px; font-size:12px;">
                        ${classification.type} (${(classification.confidence * 100).toFixed(0)}%)
                    </span>
                </div>
            </div>

            <!-- Severity Alert Banner -->
            ${getSeverityBanner(completeness.severity.severity, completeness.severity.confidence)}

            <!-- Metric Summary Cards -->
            <div class="results-summary-cards">
                <div class="summary-metric-card">
                    <span class="metric-label">Completeness score</span>
                    <span class="metric-value" style="color:var(--accent-cyan);">${(completeness.completeness_score * 100).toFixed(0)}%</span>
                    <span class="metric-sub">${completeness.present_fields.length} of 4 essential columns tracked</span>
                </div>
                <div class="summary-metric-card">
                    <span class="metric-label">Text reduction</span>
                    <span class="metric-value" style="color:var(--accent-green);">${metrics.reduction_percent}%</span>
                    <span class="metric-sub">BART Compression Ratio: ${metrics.compression_ratio}</span>
                </div>
            </div>

            <!-- Main Split Layout -->
            <div class="results-split-layout">
                <!-- Left panel: Summaries + Chatbot -->
                <div style="display:flex; flex-direction:column; gap:24px;">
                    <div class="panel summaries-card" style="padding: 20px;">
                        <div class="card-title-row">
                            <h3 style="font-family:'Outfit';">Document Summaries</h3>
                            <div class="summary-tabs">
                                <button class="summary-tab-btn active" id="tab-btn-original" onclick="switchTab('original')">Original</button>
                                <button class="summary-tab-btn" id="tab-btn-anonymized" onclick="switchTab('anonymized')">Anonymized (Redacted)</button>
                            </div>
                        </div>
                        <div id="summary-original-tab" class="tab-pane active">${data.summary}</div>
                        <div id="summary-anonymized-tab" class="tab-pane">${data.summary_anonymized}</div>
                    </div>

                    <!-- Chatbot Card -->
                    <div class="chatbot-card">
                        <div class="panel-header">
                            <h3 style="font-family:'Outfit'; font-size:16px;">AI Regulatory Assistant</h3>
                            <p style="font-size:12px; color:var(--text-secondary); margin-bottom:0;">Ask questions about this document (Llama-3-8B-Instruct)</p>
                        </div>
                        <div class="chat-history" id="chat-history">
                            <div class="chat-message message-bot">
                                Hello! I have indexed the document. Ask me any questions about the trial findings, safety issues, patient demographics, or regulatory metrics.
                            </div>
                        </div>
                        <div class="chat-input-bar">
                            <input type="text" id="chat-text-input" class="chat-text-input" placeholder="Type your question about the report..." onkeydown="handleChatKey(event)">
                            <button class="chat-send-btn" onclick="sendChatMessage()">
                                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" style="width:16px; height:16px;">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 19l9-2-9-18-9 18 9 2zm0 0v-8" />
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Right panel: checklists and duplicate details -->
                <div style="display:flex; flex-direction:column; gap:24px;">
                    <div class="panel" style="padding: 20px;">
                        <div class="panel-header" style="margin-bottom:16px;">
                            <h3 style="font-family:'Outfit'; font-size:16px;">Regulatory Field Checklist</h3>
                        </div>
                        <div class="completeness-grid">
                            ${getFieldChecklistItem('Patient Identity', completeness.present_fields.includes('patient'))}
                            ${getFieldChecklistItem('Prescribed Medication', completeness.present_fields.includes('drug'))}
                            ${getFieldChecklistItem('Adverse Incident Event', completeness.present_fields.includes('adverse_event'))}
                            ${getFieldChecklistItem('Reporting Medical Doctor', completeness.present_fields.includes('doctor'))}
                        </div>
                    </div>

                    ${getDuplicateAndComparisonSection(data.duplicate, data.comparison)}
                </div>
            </div>

            <!-- Bottom Actions -->
            <div class="results-actions-bar">
                <a href="/download/${data.pdf_file}" target="_blank" style="text-decoration:none;">
                    <button class="btn btn-success">
                        <svg class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                        <span>Download PDF Regulatory Report</span>
                    </button>
                </a>
            </div>
        </div>
    `;
    
    // Animate similarity fill bar if elements are drawn
    setTimeout(() => {
        const fillBar = document.getElementById("similarity-fill-bar");
        if (fillBar && data.duplicate && data.duplicate !== "Not Compared") {
            const pct = Math.round(data.duplicate.similarity_score * 100);
            fillBar.style.width = `${pct}%`;
        }
    }, 100);
}

function getFieldChecklistItem(label, isPresent) {
    const icon = isPresent 
        ? `<svg class="status-icon status-present" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`
        : `<svg class="status-icon status-missing" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`;
    const statusText = isPresent ? 'Present' : 'Missing';
    const statusClass = isPresent ? 'status-present' : 'status-missing';
    return `
        <div class="completeness-item">
            <span class="completeness-label">${label}</span>
            <span class="completeness-status ${statusClass}">${icon} ${statusText}</span>
        </div>
    `;
}

function getSeverityBanner(severity, confidence) {
    let typeClass = 'severity-info';
    let label = 'Clinical Severity: Mild';
    let desc = `General clinical details. Severity classified as **${severity.toUpperCase()}** (${(confidence*100).toFixed(0)}% confidence).`;
    
    const sev = severity.toLowerCase();
    if (['death', 'serious adverse event'].includes(sev)) {
        typeClass = 'severity-death';
        label = 'Critical Safety Flag';
        desc = `Serious Clinical Incident: Severity classified as **${severity.toUpperCase()}** (${(confidence*100).toFixed(0)}% confidence). Review immediately.`;
    } else if (['life threatening', 'hospitalization'].includes(sev)) {
        typeClass = 'severity-warning';
        label = 'Urgent Notice';
        desc = `Clinical Escalation: Severity classified as **${severity.toUpperCase()}** (${(confidence*100).toFixed(0)}% confidence).`;
    }
    
    return `
        <div class="severity-banner ${typeClass}">
            <svg class="severity-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div>
                <strong style="display:block; font-size:13px; text-transform:uppercase; margin-bottom:2px;">${label}</strong>
                <span style="font-size:12px; opacity:0.95;">${desc}</span>
            </div>
        </div>
    `;
}

function getDuplicateAndComparisonSection(duplicate, comparison) {
    if (!duplicate || duplicate === "Not Compared") {
        return "";
    }
    
    const percentage = Math.round(duplicate.similarity_score * 100);
    let colorClass = 'var(--accent-green)';
    if (percentage > 85) { colorClass = 'var(--accent-rose)'; }
    else if (percentage > 70) { colorClass = 'var(--accent-amber)'; }
    
    let addedHTML = "";
    let removedHTML = "";
    let modifiedHTML = "";
    
    if (comparison && comparison !== "No comparison document uploaded") {
        if (comparison.added && comparison.added.length > 0) {
            addedHTML = comparison.added.map(item => `<div class="change-item change-added">+ ${item}</div>`).join('');
        } else {
            addedHTML = '<div class="empty-changes">No added segments.</div>';
        }
        
        if (comparison.removed && comparison.removed.length > 0) {
            removedHTML = comparison.removed.map(item => `<div class="change-item change-removed">- ${item}</div>`).join('');
        } else {
            removedHTML = '<div class="empty-changes">No removed segments.</div>';
        }
        
        if (comparison.modified && comparison.modified.length > 0) {
            modifiedHTML = comparison.modified.map(item => `
                <div class="change-item change-modified">
                    <div class="change-item-old">Was: ${item.old}</div>
                    <div>Now: ${item.new}</div>
                </div>
            `).join('');
        } else {
            modifiedHTML = '<div class="empty-changes">No modified segments.</div>';
        }
    }
    
    return `
        <div class="panel" style="padding: 20px;">
            <div class="panel-header" style="margin-bottom: 12px;">
                <h3 style="font-family:'Outfit'; font-size:16px;">Lineage & Similarity Check</h3>
            </div>
            
            <div class="duplicate-gauge-container">
                <span class="metric-label">Document Cosine Match</span>
                <div class="duplicate-bar-bg">
                    <div class="duplicate-bar-fill" id="similarity-fill-bar" style="width: 0%; background: ${colorClass};"></div>
                </div>
                <div class="duplicate-match-text" style="color: ${colorClass}; font-size:14px; font-weight:700;">
                    ${percentage}% Match (${duplicate.confidence} Confidence)
                </div>
            </div>
            
            <div class="comparison-container">
                <div>
                    <h4 class="change-category-title" style="color:var(--accent-green)">Added Sentences</h4>
                    <div class="change-list">${addedHTML}</div>
                </div>
                <div>
                    <h4 class="change-category-title" style="color:var(--accent-rose)">Removed Sentences</h4>
                    <div class="change-list">${removedHTML}</div>
                </div>
                <div>
                    <h4 class="change-category-title" style="color:var(--accent-amber)">Modified Sentences</h4>
                    <div class="change-list">${modifiedHTML}</div>
                </div>
            </div>
        </div>
    `;
}

function switchTab(type) {
    const originalBtn = document.getElementById("tab-btn-original");
    const anonymizedBtn = document.getElementById("tab-btn-anonymized");
    const originalTab = document.getElementById("summary-original-tab");
    const anonymizedTab = document.getElementById("summary-anonymized-tab");
    
    if (!originalBtn || !anonymizedBtn || !originalTab || !anonymizedTab) return;
    
    if (type === 'original') {
        originalBtn.classList.add('active');
        anonymizedBtn.classList.remove('active');
        originalTab.classList.add('active');
        anonymizedTab.classList.remove('active');
    } else {
        originalBtn.classList.remove('active');
        anonymizedBtn.classList.add('active');
        originalTab.classList.remove('active');
        anonymizedTab.classList.add('active');
    }
}
window.switchTab = switchTab;

async function sendChatMessage() {
    const input = document.getElementById("chat-text-input");
    const history = document.getElementById("chat-history");
    
    if (!input || !history) return;
    
    const text = input.value.trim();
    if (!text) return;
    
    // Append user message
    history.innerHTML += `
        <div class="chat-message message-user">${escapeHtml(text)}</div>
    `;
    input.value = "";
    history.scrollTop = history.scrollHeight;
    
    // Append bot typing bubble
    const typingId = "bot-typing-" + Date.now();
    history.innerHTML += `
        <div class="chat-message message-bot" id="${typingId}">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        </div>
    `;
    history.scrollTop = history.scrollHeight;
    
    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ question: text })
        });
        
        const bubble = document.getElementById(typingId);
        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || "Server error");
        }
        
        const data = await response.json();
        if (bubble) {
            bubble.innerHTML = data.answer.replace(/\n/g, "<br>");
        }
    } catch(err) {
        const bubble = document.getElementById(typingId);
        if (bubble) {
            bubble.style.color = "var(--accent-rose)";
            bubble.innerHTML = "Error: " + err.message;
        }
    }
    history.scrollTop = history.scrollHeight;
}

function handleChatKey(event) {
    if (event.key === "Enter") {
        sendChatMessage();
    }
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

window.sendChatMessage = sendChatMessage;
window.handleChatKey = handleChatKey;