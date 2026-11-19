// State variables
let allJobs = [];
let activeIndiaOnly = true; // Default: Only show gigs applicable from India in English & Hindi!
let activeTier = 'all';
let activeCategory = 'all';
let activeCompany = 'all';
let activeExp = 3; // Default: show gigs matching Ankit's <= 3 years experience!
let allCompanies = [];
let currentSession = null;
let currentJobForInterview = null;
let currentAppPack = null;
let currentTailoredResume = null;
let allPersonas = [];
let debounceTimer = null;

// On load
document.addEventListener('DOMContentLoaded', () => {
    loadSettings();
    loadProfile();
    loadPersonas();
    checkWhisperSupport();
    loadCompanies();
    loadJobs();
});

// Load jobs from API
async function loadJobs() {
    try {
        const queryParams = new URLSearchParams();
        if (activeIndiaOnly) queryParams.append('india_only', 'true');
        if (activeTier !== 'all') queryParams.append('tier', activeTier);
        if (activeCategory !== 'all') queryParams.append('category', activeCategory);
        if (activeCompany !== 'all') queryParams.append('company', activeCompany);
        if (activeExp !== 'all') queryParams.append('max_exp', activeExp);
        
        const searchVal = document.getElementById('input-search').value.trim();
        if (searchVal) queryParams.append('search', searchVal);

        const res = await fetch(`/api/jobs?${queryParams.toString()}`);
        const data = await res.json();
        allJobs = data.jobs || [];

        // Refresh live dashboard metrics
        updateDashboardMetrics();

        // If zero jobs in DB, auto-trigger first scan
        if (allJobs.length === 0 && !searchVal && activeTier === 'all' && activeCategory === 'all' && activeCompany === 'all' && activeExp === 'all' && !activeIndiaOnly) {
            await triggerScan();
            return;
        }

        renderJobs(allJobs);
    } catch (e) {
        console.error("Failed to load jobs", e);
        showToast("Error loading gigs: " + e.message);
    }
}

// Render Job Cards
function renderJobs(jobs) {
    const container = document.getElementById('jobs-container');
    const emptyState = document.getElementById('empty-state');
    const totalCountEl = document.getElementById('count-total');
    const matchCountEl = document.getElementById('count-matched');

    totalCountEl.textContent = jobs.length;
    const highMatchCount = jobs.filter(j => j.match_score >= 70).length;
    matchCountEl.textContent = highMatchCount;

    if (jobs.length === 0) {
        container.innerHTML = '';
        emptyState.classList.remove('hidden');
        return;
    }

    emptyState.classList.add('hidden');

    container.innerHTML = jobs.map(job => {
        // Tier color
        let tierColor = 'bg-slate-800 text-slate-300 border-slate-700';
        const tierStr = job.tier || '';
        if (tierStr.includes('Microtask')) {
            tierColor = 'bg-emerald-950/70 text-emerald-300 border-emerald-800/80';
        } else if (tierStr.includes('Mid-Tier')) {
            tierColor = 'bg-blue-950/70 text-blue-300 border-blue-800/80';
        } else if (tierStr.includes('Expert')) {
            tierColor = 'bg-purple-950/70 text-purple-300 border-purple-800/80';
        }

        // Interview badge
        let interviewIcon = 'bot';
        let interviewColor = 'text-amber-400 bg-amber-950/50 border-amber-800/60';
        if (job.requires_interview.includes('Direct')) {
            interviewIcon = 'zap';
            interviewColor = 'text-emerald-400 bg-emerald-950/50 border-emerald-800/60';
        } else if (job.requires_interview.includes('Test')) {
            interviewIcon = 'file-code';
            interviewColor = 'text-cyan-400 bg-cyan-950/50 border-cyan-800/60';
        }

        // Match Score pill
        let matchScoreClass = 'bg-slate-800 text-slate-400 border-slate-700';
        if (job.match_score >= 80) {
            matchScoreClass = 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
        } else if (job.match_score >= 50) {
            matchScoreClass = 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40';
        }

        // Status badge
        const isApplied = job.application_status === 'applied';

        return `
        <div class="job-card bg-slate-900/80 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between shadow-sm relative group">
            <div class="space-y-3">
                <!-- Header row: Company & Badges -->
                <div class="flex items-start justify-between gap-2">
                    <div>
                        <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">${escapeHtml(job.company)}</span>
                        <h3 class="text-base font-bold text-slate-100 group-hover:text-indigo-300 transition line-clamp-1">${escapeHtml(job.title)}</h3>
                    </div>
                    <button onclick="toggleSave('${job.id}')" class="text-slate-500 hover:text-amber-400 transition p-1">
                        <i data-lucide="bookmark" class="w-4 h-4 ${job.is_saved ? 'fill-amber-400 text-amber-400' : ''}"></i>
                    </button>
                </div>

                <!-- Badges: Compensation, Location, Language & Requirements -->
                <div class="flex flex-wrap items-center gap-1.5 text-xs">
                    <span class="px-2.5 py-0.5 rounded-full font-semibold border ${tierColor}">
                        ${escapeHtml(job.compensation)}
                    </span>

                    <!-- India Location Status Badge -->
                    ${job.is_india_eligible ? `
                    <span class="px-2.5 py-0.5 rounded-full font-semibold border bg-emerald-950/70 text-emerald-300 border-emerald-800/80 flex items-center space-x-1" title="Applicable from India: ${escapeHtml(job.location_status || 'India Remote')}">
                        <i data-lucide="globe" class="w-3 h-3 text-emerald-400"></i>
                        <span>🇮🇳 ${escapeHtml(job.location_status || 'India / Remote')}</span>
                    </span>
                    ` : `
                    <span class="px-2.5 py-0.5 rounded-full font-medium border bg-rose-950/50 text-rose-300 border-rose-800/60 flex items-center space-x-1" title="Ineligible from India: ${escapeHtml(job.location_status || job.location)}">
                        <i data-lucide="map-pin-off" class="w-3 h-3 text-rose-400"></i>
                        <span>🚫 ${escapeHtml(job.location || 'Foreign Location')}</span>
                    </span>
                    `}

                    <span class="px-2.5 py-0.5 rounded-full font-medium border flex items-center space-x-1 ${interviewColor}">
                        <i data-lucide="${interviewIcon}" class="w-3 h-3"></i>
                        <span>${escapeHtml(job.requires_interview)}</span>
                    </span>
                    <span class="px-2.5 py-0.5 rounded-full font-medium border bg-slate-800/80 text-slate-300 border-slate-700">
                        ${escapeHtml(job.category)}
                    </span>

                    <!-- Experience requirement badge -->
                    ${job.min_exp_years <= 3 ? `
                    <span class="px-2.5 py-0.5 rounded-full font-medium border bg-indigo-950/70 text-indigo-300 border-indigo-800/80 flex items-center space-x-1" title="Fits your 2-3 years resume profile">
                        <i data-lucide="check-circle-2" class="w-3 h-3 text-indigo-400"></i>
                        <span>${escapeHtml(job.exp_label || '0-3 yrs')}</span>
                    </span>
                    ` : `
                    <span class="px-2.5 py-0.5 rounded-full font-medium border bg-slate-800/60 text-slate-400 border-slate-700/60 flex items-center space-x-1" title="Requires senior experience (risk of rejection)">
                        <i data-lucide="alert-triangle" class="w-3 h-3 text-amber-400/80"></i>
                        <span>${escapeHtml(job.exp_label || '5+ yrs')}</span>
                    </span>
                    `}
                </div>

                <!-- Match Score & Skills -->
                <div class="flex items-center justify-between text-xs pt-1">
                    <div class="flex items-center space-x-1 px-2 py-0.5 rounded-md border font-semibold ${matchScoreClass}">
                        <i data-lucide="sparkles" class="w-3 h-3"></i>
                        <span>${job.match_score}% Match</span>
                    </div>
                    <span class="text-slate-500 text-[11px]">${escapeHtml(job.location || 'Remote')}</span>
                </div>

                <!-- Matching Skills tags -->
                ${job.matching_skills && job.matching_skills.length > 0 ? `
                <div class="flex flex-wrap gap-1 text-[10px]">
                    ${job.matching_skills.slice(0, 3).map(s => `<span class="bg-slate-950 text-indigo-300 border border-slate-800 px-2 py-0.5 rounded">${escapeHtml(s)}</span>`).join('')}
                    ${job.matching_skills.length > 3 ? `<span class="text-slate-500 px-1">+${job.matching_skills.length - 3}</span>` : ''}
                </div>` : ''}

                <!-- Short description preview -->
                <p class="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                    ${escapeHtml(job.description || 'High-demand dataset annotation and evaluation contract.')}
                </p>
            </div>

            <!-- Footer Action Buttons -->
            <div class="pt-4 mt-3 border-t border-slate-800/80 flex items-center justify-between gap-2">
                <!-- 1-Click Application Pack -->
                <button onclick="openAppPackModal('${job.id}')" class="flex-1 flex items-center justify-center space-x-1 bg-slate-800 hover:bg-slate-700 text-slate-200 text-[11px] font-medium py-2 rounded-xl border border-slate-700 transition" title="Tailored answers & resume">
                    <i data-lucide="clipboard" class="w-3.5 h-3.5 text-indigo-400"></i>
                    <span>Quick Pack</span>
                </button>

                <!-- Role Interview Packet -->
                <button onclick="openInterviewPacketModal('${job.id}')" class="flex-1 flex items-center justify-center space-x-1 bg-slate-800 hover:bg-slate-700 text-slate-200 text-[11px] font-medium py-2 rounded-xl border border-slate-700 transition" title="Predicted Q&A and rubric cheatsheet">
                    <i data-lucide="book-open" class="w-3.5 h-3.5 text-amber-400"></i>
                    <span>Packet</span>
                </button>

                <!-- Interview Voice Simulator -->
                <button onclick="startInterview('${job.id}')" class="flex-1 flex items-center justify-center space-x-1 bg-indigo-600 hover:bg-indigo-500 text-white text-[11px] font-semibold py-2 rounded-xl transition shadow-indigo-600/20 shadow-sm active:scale-95" title="Start voice interview simulation">
                    <i data-lucide="mic" class="w-3.5 h-3.5"></i>
                    <span>Practice</span>
                </button>

                <!-- External Apply Link -->
                <a href="${escapeHtml(job.url)}" target="_blank" class="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition" title="Open application page">
                    <i data-lucide="external-link" class="w-3.5 h-3.5"></i>
                </a>
            </div>
        </div>
        `;
    }).join('');

    lucide.createIcons();
}

// Trigger Live Scan
async function triggerScan() {
    const btn = document.getElementById('btn-scan');
    const icon = document.getElementById('scan-icon');
    const text = document.getElementById('scan-text');

    btn.disabled = true;
    icon.classList.add('animate-spin');
    text.textContent = 'Scanning 40+ Portals...';

    try {
        const res = await fetch('/api/scan', { method: 'POST' });
        const data = await res.json();
        showToast(`Scan complete! Fetched ${data.total_jobs} active gigs.`);
        await loadJobs();
    } catch (e) {
        console.error(e);
        showToast('Scan failed: ' + e.message);
    } finally {
        btn.disabled = false;
        icon.classList.remove('animate-spin');
        text.textContent = 'Scan Now';
    }
}

// Search debounce
function debounceFilter() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        loadJobs();
    }, 300);
}

// Filter pills
function setTierFilter(tier) {
    activeTier = tier;
    document.querySelectorAll('.tier-pill').forEach(el => {
        if (el.getAttribute('data-tier') === tier) el.classList.add('active');
        else el.classList.remove('active');
    });
    loadJobs();
}

function setCategoryFilter(cat) {
    activeCategory = cat;
    document.querySelectorAll('.cat-pill').forEach(el => {
        if (el.getAttribute('data-cat') === cat) el.classList.add('active');
        else el.classList.remove('active');
    });
    loadJobs();
}

// Company Filter
function setCompanyFilter(company) {
    activeCompany = company;
    const selectEl = document.getElementById('select-company');
    if (selectEl) selectEl.value = company;

    document.querySelectorAll('.company-pill').forEach(el => {
        if (el.getAttribute('data-company') === company) el.classList.add('active');
        else el.classList.remove('active');
    });
    loadJobs();
}

// Candidate Location Filter (India Eligible Toggle)
function toggleIndiaFilter(isIndiaOnly) {
    activeIndiaOnly = isIndiaOnly;
    const btnIndia = document.getElementById('btn-india-only');
    const btnAll = document.getElementById('btn-all-locations');
    if (btnIndia && btnAll) {
        if (isIndiaOnly) {
            btnIndia.classList.add('active');
            btnAll.classList.remove('active');
        } else {
            btnIndia.classList.remove('active');
            btnAll.classList.add('active');
        }
    }
    loadCompanies();
    loadJobs();
}

// Experience Level Filter
function setExpFilter(exp) {
    activeExp = exp;
    document.querySelectorAll('.exp-pill').forEach(el => {
        const dataExp = el.getAttribute('data-exp');
        if (String(dataExp) === String(exp)) {
            el.classList.add('active');
            if (String(exp) === '3') el.classList.add('fits-resume');
        } else {
            el.classList.remove('active');
            el.classList.remove('fits-resume');
        }
    });
    loadJobs();
}

// Load company list for dropdown
async function loadCompanies() {
    try {
        const res = await fetch(`/api/companies?india_only=${activeIndiaOnly ? 'true' : 'false'}`);
        const data = await res.json();
        allCompanies = data.companies || [];

        const selectEl = document.getElementById('select-company');
        if (!selectEl) return;

        const totalGigs = allCompanies.reduce((acc, c) => acc + c.total_count, 0);
        const prefix = activeIndiaOnly ? 'India Eligible' : 'All Open';
        selectEl.innerHTML = `<option value="all">All Companies (${totalGigs} ${prefix} Gigs)</option>`;

        allCompanies.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c.company;
            opt.textContent = `${c.company} (${c.total_count} open • ${c.eligible_count} fit ≤3y)`;
            if (activeCompany === c.company) opt.selected = true;
            selectEl.appendChild(opt);
        });
    } catch (e) {
        console.error("Failed to load companies", e);
    }
}

// Update live dashboard metrics across all dimensions
async function updateDashboardMetrics() {
    try {
        const res = await fetch('/api/metrics');
        const m = await res.json();

        const totalEl = document.getElementById('count-total');
        if (totalEl) totalEl.textContent = m.total_jobs;

        const indiaCountEl = document.getElementById('count-india');
        if (indiaCountEl) indiaCountEl.textContent = m.india_eligible;

        const badgeIndiaEl = document.getElementById('badge-india-count');
        if (badgeIndiaEl) badgeIndiaEl.textContent = m.india_eligible;

        const eligibleEl = document.getElementById('count-eligible');
        if (eligibleEl) eligibleEl.textContent = m.perfect_match;
    } catch (e) {
        console.error("Metrics load failed", e);
    }
}

// Toggle Bookmark / Saved
async function toggleSave(jobId) {
    try {
        const res = await fetch(`/api/jobs/${jobId}/toggle-save`, { method: 'POST' });
        const data = await res.json();
        const job = allJobs.find(j => j.id === jobId);
        if (job) job.is_saved = data.is_saved;
        renderJobs(allJobs);
        showToast(data.is_saved ? 'Job bookmarked!' : 'Removed from bookmarks');
    } catch (e) {
        showToast('Error saving job');
    }
}

// Open 1-Click Application Pack Modal
async function openAppPackModal(jobId) {
    try {
        switchPackTab('answers'); // default to answers tab

        // Fetch application pack answers
        const res = await fetch(`/api/jobs/${jobId}/application-pack`);
        const pack = await res.json();
        currentAppPack = pack;

        document.getElementById('pack-role').textContent = `${pack.role_title} at ${pack.company}`;
        document.getElementById('pack-why').value = pack.why_interested;
        document.getElementById('pack-exp').value = pack.relevant_experience;
        document.getElementById('pack-qa').value = pack.quality_assurance_strategy;
        document.getElementById('pack-apply-link').href = pack.apply_url;

        // Fetch dynamically tailored ATS resume
        const resResume = await fetch(`/api/jobs/${jobId}/tailored-resume`);
        const resumeData = await resResume.json();
        currentTailoredResume = resumeData;
        document.getElementById('pack-tailored-resume').value = resumeData.formatted_resume;

        openModal('modal-app-pack');
    } catch (e) {
        showToast('Error generating application pack');
    }
}

// Switch tabs inside Pack Modal
function switchPackTab(tab) {
    const tabAnswers = document.getElementById('tab-content-answers');
    const tabResume = document.getElementById('tab-content-resume');
    const btnAnswers = document.getElementById('tab-btn-answers');
    const btnResume = document.getElementById('tab-btn-resume');

    if (tab === 'answers') {
        tabAnswers.classList.remove('hidden');
        tabResume.classList.add('hidden');
        btnAnswers.className = 'font-semibold text-indigo-400 border-b-2 border-indigo-500 pb-1 px-2';
        btnResume.className = 'font-semibold text-slate-400 hover:text-slate-200 pb-1 px-2';
    } else {
        tabAnswers.classList.add('hidden');
        tabResume.classList.remove('hidden');
        btnResume.className = 'font-semibold text-indigo-400 border-b-2 border-indigo-500 pb-1 px-2';
        btnAnswers.className = 'font-semibold text-slate-400 hover:text-slate-200 pb-1 px-2';
    }
}

// Copy tailored resume to clipboard
function copyTailoredResumeOnly() {
    if (!currentTailoredResume) return;
    navigator.clipboard.writeText(currentTailoredResume.formatted_resume);
    showToast('Copied tailored ATS resume to clipboard!');
}

// Copy Full Pack to Clipboard
function copyFullPack() {
    if (!currentAppPack) return;
    navigator.clipboard.writeText(currentAppPack.one_click_bundle);
    showToast('Copied full application pack & answers to clipboard!');
}

// --- ROLE INTERVIEW PACKET ---
let currentInterviewPacket = null;
let currentPacketJobId = null;

async function openInterviewPacketModal(jobId) {
    try {
        currentPacketJobId = jobId;
        showToast('Generating role interview packet...');
        const res = await fetch(`/api/jobs/${jobId}/interview-packet`);
        const packet = await res.json();
        currentInterviewPacket = packet;

        document.getElementById('packet-role-title').textContent = `${packet.role_title} Dossier`;
        document.getElementById('packet-company-subtitle').textContent = `Target Platform: ${packet.company} (${packet.category})`;
        document.getElementById('packet-focus-text').textContent = packet.company_focus;

        const qaContainer = document.getElementById('packet-qa-container');
        qaContainer.innerHTML = (packet.questions_and_answers || []).map((qa, idx) => `
            <div class="bg-slate-950 border border-slate-800 rounded-xl p-3.5 space-y-2">
                <div class="flex items-center justify-between text-xs">
                    <span class="font-bold text-indigo-400">${escapeHtml(qa.round)}</span>
                    <button onclick="copySingleQa(${idx})" class="text-[11px] text-slate-400 hover:text-white flex items-center space-x-1">
                        <i data-lucide="copy" class="w-3 h-3"></i>
                        <span>Copy Answer</span>
                    </button>
                </div>
                <p class="font-semibold text-xs text-slate-200">Q: ${escapeHtml(qa.question)}</p>
                <div class="bg-slate-900/90 border border-slate-800/80 p-2.5 rounded-lg text-xs text-slate-300 leading-relaxed">
                    <strong class="text-emerald-400 text-[11px] block mb-1">A+ Grounded Formulation:</strong>
                    "${escapeHtml(qa.winning_answer)}"
                </div>
            </div>
        `).join('');

        openModal('modal-interview-packet');
        lucide.createIcons();
    } catch (e) {
        showToast('Error loading interview packet: ' + e.message);
    }
}

function copyFullInterviewPacket() {
    if (!currentInterviewPacket) return;
    navigator.clipboard.writeText(currentInterviewPacket.full_packet_text);
    showToast('Copied full interview dossier to clipboard!');
}

function copySingleQa(idx) {
    if (!currentInterviewPacket || !currentInterviewPacket.questions_and_answers) return;
    const item = currentInterviewPacket.questions_and_answers[idx];
    if (item) {
        navigator.clipboard.writeText(item.winning_answer);
        showToast(`Copied winning answer for ${item.round}!`);
    }
}

function startInterviewFromPacket() {
    closeModal('modal-interview-packet');
    if (currentPacketJobId) {
        startInterview(currentPacketJobId);
    }
}

// --- AI INTERVIEW SIMULATOR ROOM ---

async function startInterview(jobId) {
    const job = allJobs.find(j => j.id === jobId);
    if (!job) return;
    currentJobForInterview = job;

    document.getElementById('interview-title').textContent = `${job.company} AI Interview Simulator`;
    document.getElementById('interview-role').textContent = `Role: ${job.title} (${job.requires_interview})`;
    document.getElementById('chat-history').innerHTML = `
        <div class="flex items-center justify-center p-8 text-slate-400 space-x-2 text-xs">
            <i data-lucide="loader" class="w-4 h-4 animate-spin"></i>
            <span>Initializing simulated assessment with ${escapeHtml(job.company)} Lead Interviewer...</span>
        </div>
    `;
    lucide.createIcons();
    openModal('modal-interview');

    try {
        const res = await fetch('/api/interview/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ job_id: jobId })
        });
        const session = await res.json();
        currentSession = session;
        renderInterviewState();
    } catch (e) {
        showToast('Failed to start interview: ' + e.message);
    }
}

function renderInterviewState() {
    if (!currentSession) return;

    // Update Round Stepper
    for (let i = 1; i <= 5; i++) {
        const stepEl = document.getElementById(`step-${i}`);
        if (!stepEl) continue;
        stepEl.className = 'step-badge';
        if (i < currentSession.current_round) {
            stepEl.classList.add('completed');
        } else if (i === currentSession.current_round) {
            stepEl.classList.add('active');
        }
    }

    const isOffline = currentSession.is_offline_fallback || currentSession.messages.some(m => m.evaluation_source === 'heuristic');
    const offlineBanner = document.getElementById('interview-offline-banner');
    if (offlineBanner) {
        if (isOffline) {
            offlineBanner.classList.remove('hidden');
        } else {
            offlineBanner.classList.add('hidden');
        }
    }

    if (currentSession.is_completed) {
        const scoreBadge = document.getElementById('interview-score-badge');
        scoreBadge.classList.remove('hidden');
        if (isOffline) {
            scoreBadge.className = 'font-semibold text-amber-400 bg-amber-950/60 border border-amber-800 px-2.5 py-0.5 rounded-full text-xs';
            scoreBadge.innerHTML = `Score: <span id="overall-score-val">${currentSession.overall_score}</span>/100 <span class="text-[10px] opacity-80">(Offline Heuristic)</span>`;
        } else {
            scoreBadge.className = 'font-semibold text-emerald-400 bg-emerald-950/60 border border-emerald-800 px-2.5 py-0.5 rounded-full text-xs';
            scoreBadge.innerHTML = `Score: <span id="overall-score-val">${currentSession.overall_score}</span>/100 <span class="text-[10px] opacity-80">(Frontier AI)</span>`;
        }
    } else {
        document.getElementById('interview-score-badge').classList.add('hidden');
    }

    // Render Chat Messages
    const container = document.getElementById('chat-history');
    container.innerHTML = currentSession.messages.map(m => {
        const isAi = m.sender === 'ai';
        return `
        <div class="flex flex-col ${isAi ? 'items-start' : 'items-end'} space-y-1">
            <span class="text-[10px] text-slate-500 font-semibold px-1">${isAi ? `${currentSession.company} Interviewer` : 'You (Candidate)'}</span>
            <div class="max-w-[85%] rounded-2xl p-4 text-xs leading-relaxed ${isAi ? 'bg-slate-900 border border-slate-800 text-slate-200' : 'bg-indigo-600 text-white shadow-md'}">
                <div class="whitespace-pre-line">${escapeHtml(m.message)}</div>

                ${m.feedback ? `
                <div class="mt-3 pt-2.5 border-t border-slate-800/80 text-[11px] text-indigo-300 bg-slate-950/60 p-2.5 rounded-xl">
                    <div class="flex items-center justify-between mb-1">
                        <div class="flex items-center space-x-1 font-semibold">
                            <i data-lucide="award" class="w-3.5 h-3.5 text-amber-400"></i>
                            <span>Round Score: ${m.score != null ? m.score : '—'}/10</span>
                        </div>
                        ${m.evaluation_source === 'gemini'
                            ? `<span class="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 font-medium">Frontier AI Scored</span>`
                            : m.evaluation_source === 'heuristic'
                            ? `<span class="text-[10px] px-2 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-800 font-medium">Offline Heuristic</span>`
                            : ''
                        }
                    </div>
                    <div>${escapeHtml(m.feedback)}</div>
                </div>` : ''}
            </div>
        </div>
        `;
    }).join('');

    container.scrollTop = container.scrollHeight;
    lucide.createIcons();

    // Populate hint if available
    const lastAiMsg = [...currentSession.messages].reverse().find(m => m.sender === 'ai');
    if (lastAiMsg && lastAiMsg.suggested_answer) {
        document.getElementById('hint-box').innerHTML = `
            <strong>Rubric & Ideal Answer:</strong><br>
            ${escapeHtml(lastAiMsg.suggested_answer)}
        `;
    }
}

async function sendInterviewReply() {
    const input = document.getElementById('chat-input');
    const msg = input.value.trim();
    if (!msg || !currentSession) return;

    input.value = '';
    const btn = document.getElementById('btn-send-reply');
    btn.disabled = true;

    // Optimistically render candidate reply
    currentSession.messages.push({
        sender: 'user',
        message: msg,
        round_number: currentSession.current_round
    });
    renderInterviewState();

    try {
        const res = await fetch('/api/interview/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: currentSession.session_id,
                job_id: currentSession.job_id,
                user_message: msg
            })
        });
        const updated = await res.json();
        currentSession = updated;
        renderInterviewState();
    } catch (e) {
        showToast('Error communicating with interviewer: ' + e.message);
    } finally {
        btn.disabled = false;
    }
}

function toggleHint() {
    const hint = document.getElementById('hint-box');
    hint.classList.toggle('hidden');
}

// Copy Master Prompt for external AI practice
async function copyMasterPrompt() {
    if (!currentJobForInterview) return;
    try {
        const res = await fetch(`/api/jobs/${currentJobForInterview.id}/application-pack`);
        const pack = await res.json();
        navigator.clipboard.writeText(pack.master_interview_prompt);
        showToast('Master Interview Prompt copied! Paste into Antigravity or ChatGPT to practice externally.');
    } catch (e) {
        showToast('Error copying prompt');
    }
}

// --- PROFILE & RESUME LOGIC ---

// --- PERSONAS & RESUME LOGIC ---

async function loadPersonas() {
    try {
        const res = await fetch('/api/personas');
        const data = await res.json();
        allPersonas = data.personas || [];

        const container = document.getElementById('personas-container');
        if (!container) return;

        container.innerHTML = allPersonas.map(p => {
            const isActive = p.is_active;
            return `
            <div class="p-3.5 rounded-xl border ${isActive ? 'bg-indigo-950/40 border-indigo-500 shadow-sm' : 'bg-slate-950 border-slate-800'} flex flex-col justify-between space-y-2">
                <div>
                    <div class="flex items-center justify-between gap-2">
                        <h4 class="font-bold text-xs ${isActive ? 'text-indigo-300' : 'text-slate-200'}">${escapeHtml(p.title)}</h4>
                        ${isActive ? '<span class="text-[10px] bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 px-2 py-0.5 rounded-full font-semibold">Active</span>' : ''}
                    </div>
                    <p class="text-[11px] text-slate-400 mt-1 line-clamp-2">${escapeHtml(p.summary)}</p>
                </div>
                <div class="flex items-center justify-between pt-2 border-t border-slate-800/60">
                    <span class="text-[10px] text-slate-500">${(p.skills || []).slice(0, 3).join(', ')}...</span>
                    ${!isActive ? `
                    <button onclick="activatePersona('${p.id}')" class="text-xs bg-slate-800 hover:bg-indigo-600 text-slate-200 hover:text-white px-2.5 py-1 rounded-lg transition font-medium">
                        Switch
                    </button>` : '<span class="text-[11px] text-emerald-400 font-semibold">In Use</span>'}
                </div>
            </div>
            `;
        }).join('');
    } catch (e) {
        console.error("Failed to load personas", e);
    }
}

async function activatePersona(personaId) {
    try {
        showToast('Switching active resume persona...');
        const res = await fetch(`/api/personas/${personaId}/activate`, { method: 'POST' });
        await res.json();
        await loadPersonas();
        await loadProfile();
        await loadJobs();
        showToast('Persona activated! Re-scored 510 jobs with new skills.');
    } catch (e) {
        showToast('Error activating persona');
    }
}

async function loadProfile() {
    try {
        const res = await fetch('/api/profile');
        const profile = await res.json();
        document.getElementById('profile-skills').value = (profile.skills || []).join(', ');
        document.getElementById('profile-text').value = profile.resume_text || '';
    } catch (e) {
        console.error("Failed to load profile", e);
    }
}

async function saveUserProfile() {
    const skills = document.getElementById('profile-skills').value.split(',').map(s => s.trim()).filter(Boolean);
    const resume_text = document.getElementById('profile-text').value;

    try {
        await fetch('/api/profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: 'Candidate',
                skills: skills,
                resume_text: resume_text
            })
        });
        closeModal('modal-resume');
        showToast('Profile updated & skills saved!');
        await loadJobs(); // Re-rank with updated skills
    } catch (e) {
        showToast('Error saving profile');
    }
}

async function uploadResumeFile(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    showToast(`Parsing ${file.name}...`);

    try {
        const res = await fetch('/api/profile/upload-resume', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        showToast(data.message);
        await loadProfile();
        await loadJobs();
    } catch (e) {
        showToast('Failed to parse resume: ' + e.message);
    }
}

// --- SETTINGS LOGIC ---

async function loadSettings() {
    try {
        const res = await fetch('/api/settings');
        const settings = await res.json();
        if (settings.gemini_api_key_set) {
            document.getElementById('setting-gemini-key').placeholder = settings.gemini_api_key_masked;
        }
        document.getElementById('setting-model').value = settings.gemini_model || 'gemini-2.5-flash';
        document.getElementById('setting-offline').checked = settings.offline_mode;
    } catch (e) {
        console.error("Failed to load settings", e);
    }
}

async function saveAppSettings() {
    const key = document.getElementById('setting-gemini-key').value.trim();
    const model = document.getElementById('setting-model').value;
    const offline = document.getElementById('setting-offline').checked;

    try {
        await fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                gemini_api_key: key || undefined,
                gemini_model: model,
                offline_mode: offline
            })
        });
        closeModal('modal-settings');
        showToast('AI Settings updated successfully!');
    } catch (e) {
        showToast('Error saving settings');
    }
}

// --- MODAL UTILITIES ---

function openModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.classList.remove('hidden');
        setTimeout(() => {
            if (window.lucide) lucide.createIcons();
        }, 50);
    }
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.add('hidden');
}

function showToast(msg) {
    const toast = document.getElementById('toast');
    const msgEl = document.getElementById('toast-msg');
    msgEl.textContent = msg;
    toast.classList.remove('hidden');
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3500);
}

function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// --- VOICE & WHISPER RECOGNITION CONTROLLER ---

let speechRecognizer = null;
let isRecording = false;
let mediaRecorder = null;
let audioChunks = [];

function checkWhisperSupport() {
    fetch('/api/whisper-status')
        .then(r => r.json())
        .then(data => {
            const badge = document.getElementById('whisper-badge');
            if (!badge) return;
            if (data.local_whisper_online) {
                badge.innerHTML = `<i data-lucide="zap" class="w-3 h-3 text-emerald-400"></i><span>Local Whisper (Port 8178) Online</span>`;
            } else if (data.groq_whisper_available) {
                badge.innerHTML = `<i data-lucide="zap" class="w-3 h-3 text-cyan-400"></i><span>Groq Whisper Active</span>`;
            } else {
                badge.innerHTML = `<i data-lucide="mic" class="w-3 h-3 text-emerald-400"></i><span>Browser Voice STT Ready</span>`;
            }
            lucide.createIcons();
        })
        .catch(() => {});
}

function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return null;

    const recognizer = new SpeechRecognition();
    recognizer.continuous = true;
    recognizer.interimResults = true;
    recognizer.lang = 'en-US';

    recognizer.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
            transcript += event.results[i][0].transcript;
        }
        const input = document.getElementById('chat-input');
        if (input && transcript) {
            if (event.results[event.results.length - 1].isFinal) {
                input.value = (input.value ? input.value.trim() + ' ' : '') + transcript.trim();
            }
        }
    };

    recognizer.onerror = (event) => {
        console.warn('Speech recognition notice:', event.error);
        if (event.error !== 'no-speech') {
            stopVoiceInput();
        }
    };

    recognizer.onend = () => {
        if (isRecording) {
            try { recognizer.start(); } catch(e) {}
        }
    };

    return recognizer;
}

function toggleVoiceInput() {
    if (isRecording) {
        stopVoiceInput();
    } else {
        startVoiceInput();
    }
}

async function startVoiceInput() {
    const input = document.getElementById('chat-input');
    const banner = document.getElementById('voice-banner');
    const micLabel = document.getElementById('mic-label');
    const btnMic = document.getElementById('btn-mic');

    // 1. Try Browser Web Speech API (real-time zero latency)
    if (!speechRecognizer) {
        speechRecognizer = initSpeechRecognition();
    }

    if (speechRecognizer) {
        try {
            speechRecognizer.start();
            isRecording = true;
            if (banner) banner.classList.remove('hidden');
            if (micLabel) micLabel.textContent = 'Stop';
            if (btnMic) {
                btnMic.classList.remove('bg-slate-800');
                btnMic.classList.add('bg-rose-600', 'animate-pulse');
            }
            showToast('Microphone listening! Speak your answer naturally.');
            return;
        } catch (e) {
            console.warn('Web Speech start error, trying MediaRecorder fallback', e);
        }
    }

    // 2. MediaRecorder fallback to /api/transcribe
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            audioChunks = [];
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);
            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const formData = new FormData();
                formData.append('file', audioBlob, 'candidate_voice.wav');
                showToast('Transcribing audio via Whisper...');
                try {
                    const res = await fetch('/api/transcribe', { method: 'POST', body: formData });
                    const data = await res.json();
                    if (data.text) {
                        input.value = (input.value ? input.value.trim() + ' ' : '') + data.text.trim();
                        showToast('Voice transcribed successfully!');
                    }
                } catch (err) {
                    showToast('Transcription failed: ' + err.message);
                }
            };

            mediaRecorder.start();
            isRecording = true;
            if (banner) banner.classList.remove('hidden');
            if (micLabel) micLabel.textContent = 'Stop';
            if (btnMic) {
                btnMic.classList.remove('bg-slate-800');
                btnMic.classList.add('bg-rose-600', 'animate-pulse');
            }
            showToast('Recording voice... Speak your answer.');
        } catch (err) {
            showToast('Microphone access denied or not available.');
        }
    } else {
        showToast('Voice input is not supported in this browser. Please use Chrome or Edge.');
    }
}

function stopVoiceInput() {
    isRecording = false;
    const banner = document.getElementById('voice-banner');
    const micLabel = document.getElementById('mic-label');
    const btnMic = document.getElementById('btn-mic');

    if (banner) banner.classList.add('hidden');
    if (micLabel) micLabel.textContent = 'Speak';
    if (btnMic) {
        btnMic.classList.remove('bg-rose-600', 'animate-pulse');
        btnMic.classList.add('bg-slate-800');
    }

    if (speechRecognizer) {
        try { speechRecognizer.stop(); } catch(e) {}
    }

    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
    }
}
