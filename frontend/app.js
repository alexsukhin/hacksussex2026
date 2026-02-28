// ─── CONFIG ──────────────────────────────────────────────────

const API_URL     = 'http://127.0.0.1:8000/readings/';
const WEATHER_URL = 'http://127.0.0.1:8000/weather/hourly';

const CROPS = {
    wheat:       { label: 'Wheat',          idealMoisture: 55, idealLight: 600, emoji: '🌾' },
    barley:      { label: 'Barley',         idealMoisture: 50, idealLight: 650, emoji: '🌾' },
    oats:        { label: 'Oats',           idealMoisture: 60, idealLight: 580, emoji: '🌾' },
    potatoes:    { label: 'Potatoes',       idealMoisture: 75, idealLight: 500, emoji: '🥔' },
    rapeseed:    { label: 'Rapeseed',       idealMoisture: 50, idealLight: 700, emoji: '🌼' },
    sugar_beet:  { label: 'Sugar Beet',     idealMoisture: 65, idealLight: 600, emoji: '🌿' },
    field_beans: { label: 'Field Beans',    idealMoisture: 65, idealLight: 550, emoji: '🫘' },
    peas:        { label: 'Peas',           idealMoisture: 60, idealLight: 580, emoji: '🟢' },
    maize:       { label: 'Maize (Silage)', idealMoisture: 70, idealLight: 750, emoji: '🌽' },
    other:       { label: 'Other',          idealMoisture: 60, idealLight: 600, emoji: '🌱' },
};

const CROP_REQ_TEXT = {
    wheat:       'Moisture: 55% | Light: 600 lux | Frost-hardy, well-drained soil',
    barley:      'Moisture: 50% | Light: 650 lux | Drought-tolerant, low N required',
    oats:        'Moisture: 60% | Light: 580 lux | Tolerates wet conditions well',
    potatoes:    'Moisture: 75% | Light: 500 lux | High water demand, avoid waterlogging',
    rapeseed:    'Moisture: 50% | Light: 700 lux | High light demand, nitrogen-fixing',
    sugar_beet:  'Moisture: 65% | Light: 600 lux | Long season, moderate water need',
    field_beans: 'Moisture: 65% | Light: 550 lux | Good companion crop, fixes nitrogen',
    peas:        'Moisture: 60% | Light: 580 lux | Cool season crop, well-drained soil',
    maize:       'Moisture: 70% | Light: 750 lux | Needs warmth and high light levels',
    other:       'Moisture: 60% | Light: 600 lux | Custom crop — defaults applied',
};

// Maps backend plot_id → grid cell index
const ZONES_BACKEND = {
    "8b3e3560-cb9d-4ebf-8571-d69a2191bbfa": 0,
    "bef10565-2068-4d00-8c89-1e79f359048b": 1,
    "27afa7d4-1a5c-451a-b72b-c70a60e4eb5d": 2,
    "28b31c76-7597-4206-ab54-b004f122b022": 3,
};

// ─── STATE ───────────────────────────────────────────────────

const GRID_SIZE = 9; // 3×3

let cells = Array.from({ length: GRID_SIZE }, (_, i) => ({
    id: i,
    name: `Zone ${i + 1}`,
    crop: null,
    moisture: null,
    light: null,
    score: null,
    status: 'unset',
    color: 'unset',
    address: '',
    idealMoisture: null,
    idealLight: null,
}));

let selectedCells = new Set();
let isDragging    = false;
let dragStart     = null;
let rainExpected  = false;

// ─── STATUS LOGIC ────────────────────────────────────────────

function recalcStatus(i) {
    const cell = cells[i];
    if (cell.moisture === null || !cell.idealMoisture) {
        cell.status = 'unset'; cell.color = 'unset'; cell.score = null;
        return;
    }
    const score = Math.round((cell.moisture / cell.idealMoisture) * 100);
    cell.score = score;
    if      (score < 80)  { cell.status = 'dry';           cell.color = 'red';   }
    else if (score > 120) { cell.status = 'oversaturated'; cell.color = 'blue';  }
    else                  { cell.status = 'optimal';       cell.color = 'green'; }
}

// ─── RENDER: GRID ────────────────────────────────────────────

function renderGrid() {
    const grid = document.getElementById('field-grid');
    grid.innerHTML = '';

    cells.forEach((cell, i) => {
        const el = document.createElement('div');
        el.className = `field-cell status-${cell.status}`;
        el.dataset.index = i;
        if (selectedCells.has(i)) el.classList.add('is-selected');

        const cropInfo = cell.crop ? CROPS[cell.crop] : null;
        el.innerHTML = `
            <div class="cell-status-dot"></div>
            <div class="cell-label">
                <div class="cell-crop">${cropInfo ? cropInfo.emoji + ' ' + cropInfo.label : cell.name}</div>
                <div class="cell-moisture">${cell.moisture !== null ? '💧 ' + cell.moisture + '%' : '— unset'}</div>
            </div>
        `;

        el.addEventListener('mousedown',  e => { e.preventDefault(); startDrag(i); });
        el.addEventListener('mouseenter', ()  => { if (isDragging) extendDrag(i); });
        el.addEventListener('mouseup',    ()  => endDrag());
        el.addEventListener('touchstart', e => { e.preventDefault(); startDrag(i); }, { passive: false });
        el.addEventListener('touchmove',  e => {
            e.preventDefault();
            const t = e.touches[0];
            const target = document.elementFromPoint(t.clientX, t.clientY);
            if (target?.dataset?.index) extendDrag(parseInt(target.dataset.index));
        }, { passive: false });
        el.addEventListener('touchend', () => endDrag());

        grid.appendChild(el);
    });
}

// ─── RENDER: STATS ───────────────────────────────────────────

function renderStats() {
    const table = document.getElementById('zone-table');
    table.innerHTML = cells.map(cell => {
        const dotColor  = cell.status === 'optimal' ? '#2ecc71' : cell.status === 'dry' ? '#e74c3c' : cell.status === 'oversaturated' ? '#3498db' : '#aaa';
        const barColor  = cell.status === 'optimal' ? '#2ecc71' : cell.status === 'dry' ? '#e74c3c' : '#3498db';
        const scoreWidth = cell.score ? Math.min(100, cell.score) : 0;
        const cropLabel  = cell.crop ? `${CROPS[cell.crop]?.emoji} ${CROPS[cell.crop]?.label}` : '—';
        return `
            <div class="zone-row">
                <div class="zone-dot" style="background:${dotColor}"></div>
                <div class="zone-name">${cell.name}</div>
                <div class="zone-crop">${cropLabel}</div>
                <div class="score-bar-wrap"><div class="score-bar" style="width:${scoreWidth}%;background:${barColor}"></div></div>
                <div class="zone-score" style="color:${dotColor}">${cell.score !== null ? cell.score + '%' : '—'}</div>
                <div style="font-size:0.65rem;color:var(--muted);min-width:5rem;text-align:right">
                    ${cell.moisture !== null ? '💧' + cell.moisture + '% ☀️' + cell.light : 'no data'}
                </div>
            </div>
        `;
    }).join('');
}

// ─── RENDER: ALERTS ──────────────────────────────────────────

function renderAlerts() {
    const list   = document.getElementById('alerts-list');
    const alerts = [];

    cells.forEach(cell => {
        if (cell.status === 'dry' && cell.crop) {
            if (rainExpected) {
                alerts.push({ icon: '🌧', text: `${cell.name} (${CROPS[cell.crop]?.label}) is dry — rain forecast, watering suppressed`, time: 'Suppressed' });
            } else {
                alerts.push({ icon: '🔴', text: `${cell.name} (${CROPS[cell.crop]?.label}) needs water now! Moisture: ${cell.moisture}%`, time: 'Now' });
            }
        }
        if (cell.status === 'oversaturated') {
            alerts.push({ icon: '🔵', text: `${cell.name} oversaturated — risk of root rot. Moisture: ${cell.moisture}%`, time: 'Now' });
        }
    });

    list.innerHTML = alerts.length === 0
        ? '<div class="no-alerts">✅ No alerts — all zones nominal</div>'
        : alerts.map(a => `
            <div class="alert-item">
                <span class="alert-icon">${a.icon}</span>
                <div>
                    <div class="alert-text">${a.text}</div>
                    <div class="alert-time">${a.time}</div>
                </div>
            </div>
          `).join('');
}

// ─── DRAG SELECTION ──────────────────────────────────────────

function startDrag(i) {
    isDragging = true;
    dragStart  = i;
    selectedCells.clear();
    selectedCells.add(i);
    renderGrid();
    updateEditor();
}

function extendDrag(i) {
    if (!isDragging) return;
    const cols = 3;
    const r1 = Math.floor(dragStart / cols), c1 = dragStart % cols;
    const r2 = Math.floor(i / cols),         c2 = i % cols;
    const minR = Math.min(r1, r2), maxR = Math.max(r1, r2);
    const minC = Math.min(c1, c2), maxC = Math.max(c1, c2);
    selectedCells.clear();
    for (let r = minR; r <= maxR; r++)
        for (let c = minC; c <= maxC; c++)
            selectedCells.add(r * cols + c);
    renderGrid();
    updateEditor();
}

function endDrag() { isDragging = false; }

document.addEventListener('mouseup', endDrag);

// ─── EDITOR ──────────────────────────────────────────────────

function updateEditor() {
    const editor   = document.getElementById('crop-editor');
    const prompt   = document.getElementById('editor-prompt');
    const selCount = document.getElementById('sel-count');

    if (selectedCells.size === 0) {
        editor.classList.remove('active');
        selCount.textContent = '';
        return;
    }

    editor.classList.add('active');
    selCount.textContent = `${selectedCells.size} zone${selectedCells.size > 1 ? 's' : ''} selected`;
    prompt.textContent   = `Editing ${selectedCells.size} zone${selectedCells.size > 1 ? 's' : ''}. Configure below and click Apply.`;

    // Pre-fill dropdown if all selected share the same crop
    const unique = [...new Set([...selectedCells].map(i => cells[i].crop).filter(Boolean))];
    if (unique.length === 1) {
        document.getElementById('crop-select').value = unique[0];
        updateCropReq();
    }
}

function updateCropReq() {
    const val = document.getElementById('crop-select').value;
    document.getElementById('crop-req').textContent =
        val ? CROP_REQ_TEXT[val] : 'Select a crop to see moisture & light requirements.';
}

function applyToSelected() {
    const crop = document.getElementById('crop-select').value;
    if (!crop) { showToast('Please select a crop type first.'); return; }

    selectedCells.forEach(i => {
        cells[i].crop          = crop;
        cells[i].idealMoisture = CROPS[crop].idealMoisture;
        cells[i].idealLight    = CROPS[crop].idealLight;
        if (cells[i].moisture !== null) recalcStatus(i);
    });

    renderGrid();
    renderStats();
    renderAlerts();
    showToast(`✓ Applied ${CROPS[crop].label} to ${selectedCells.size} zone${selectedCells.size > 1 ? 's' : ''}`);
    selectedCells.clear();
    updateEditor();
}

function clearSelection() {
    selectedCells.clear();
    renderGrid();
    updateEditor();
}

document.getElementById('crop-select').addEventListener('change', updateCropReq);

// ─── API: READINGS ────────────────────────────────────────────

async function fetchReadings() {
    try {
        const resp = await fetch(API_URL);
        if (!resp.ok) return;
        const data = await resp.json();

        // Take the most recent reading per plot
        const latest = {};
        data.forEach(r => { if (!latest[r.plot_id]) latest[r.plot_id] = r; });

        Object.entries(latest).forEach(([plot_id, r]) => {
            const idx = ZONES_BACKEND[plot_id];
            if (idx === undefined) return;
            cells[idx].moisture = r.moisture;
            cells[idx].light    = r.light;
            if (!cells[idx].crop) {
                cells[idx].crop          = 'wheat';
                cells[idx].idealMoisture = 55;
            }
            recalcStatus(idx);
        });

        renderGrid();
        renderStats();
        renderAlerts();
    } catch (e) { /* backend offline — fail silently */ }
}

// ─── API: WEATHER ─────────────────────────────────────────────

async function fetchWeather() {
    try {
        const resp = await fetch(WEATHER_URL);
        if (!resp.ok) return;
        const data = await resp.json();

        document.getElementById('location-label').textContent = data.location || 'UK';

        const strip = document.getElementById('weather-strip');
        strip.innerHTML = '';
        const now = new Date();

        data.hourly.forEach(h => {
            const t    = new Date(h.time);
            const pill = document.createElement('div');
            pill.className = 'hour-pill' + (Math.abs(t - now) < 3600000 ? ' current' : '');
            pill.innerHTML = `
                <span class="temp">${h.temp_c.toFixed(1)}°</span>
                <span>${t.getHours()}:00</span>
                <span class="rain">🌧${h.chance_of_rain}%</span>
            `;
            strip.appendChild(pill);
        });

        // Suppress dry alerts if heavy rain forecast within 12 hours
        rainExpected = data.hourly
            .filter(h => { const t = new Date(h.time); return t > now && t < new Date(+now + 12 * 3600000); })
            .some(h => h.chance_of_rain > 60);

        renderAlerts();
    } catch (e) { /* weather API offline */ }
}

// ─── UTILITIES ───────────────────────────────────────────────

function updateClock() {
    document.getElementById('clock').textContent = new Date().toLocaleTimeString('en-GB');
}

function showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 2500);
}

// ─── INIT ────────────────────────────────────────────────────

renderGrid();
renderStats();
renderAlerts();
updateClock();
fetchWeather();
fetchReadings();

setInterval(fetchReadings, 5000);
setInterval(fetchWeather,  60000);
setInterval(updateClock,   1000);