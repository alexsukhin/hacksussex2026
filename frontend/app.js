// CONFIG
const API_URL              = 'http://127.0.0.1:8000/readings/';
const WEATHER_URL          = 'http://127.0.0.1:8000/weather/hourly';
const BACKEND_WEATHER_BASE = 'http://127.0.0.1:8000/weather';
const STATS_URL            = 'http://127.0.0.1:8000/stats/summary';

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

const ZONES_BACKEND = {
    "950b5dd5-c2e6-4aeb-b2d0-8cf5b89c033e": 0,
    "03256848-ddcf-4e66-b122-30a4a0af27ac": 1,
    "4084dce6-1537-45e7-a435-05479b6c5263": 2,
    "f65f9eda-4f72-4273-bc83-014c6fc3a7d7": 3,
    "27b29098-ce21-4b11-b7e5-69d21fe96c92": 4,
    "ac02134e-594b-403f-a49d-164d04393b60": 5,
    "a72aa36a-757b-4132-b710-9dafb93ff030": 6,
    "b8a51a6b-e674-42c8-bdf6-029aa5e30c94": 7,
    "e6e36356-163d-4d79-ad3b-9a195cd6d5b8": 8,
};


const PLOT_ID_TO_NAME = Object.fromEntries(
    Object.entries(ZONES_BACKEND).map(([pid, idx]) => [pid, `Zone ${idx + 1}`])
);

let activePeriodDays = 7;
let currentLocation = { lat: 51.5074, lon: -0.1278 }; // default London
let rainExpected = false;
let blightRisk = false; // Add this line to track fungal risk

// GRID STATE
const GRID_SIZE = 9;
let cells = Array.from({ length: GRID_SIZE }, (_, i) => ({
    id: i, name: `Zone ${i+1}`, crop: null, moisture: null, light: null,
    score: null, status: 'unset', color: 'unset', address: '',
    idealMoisture: null, idealLight: null,
}));

let selectedCells = new Set();
let isDragging    = false;
let dragStart     = null;

// STATUS CALC
function recalcStatus(i) {
    const cell = cells[i];
    if (cell.moisture === null || !cell.idealMoisture) {
        cell.status = 'unset'; cell.color = 'unset'; cell.score = null; cell.waterNeeded = 0;
        return;
    }
    const score = Math.round((cell.moisture / cell.idealMoisture) * 100);
    cell.score = score;
    
    // Calculate required water volume based on moisture deficit and light levels
    if (cell.moisture < cell.idealMoisture) {
        const moistureDeficit = cell.idealMoisture - cell.moisture;
        const lightFactor = (cell.light && cell.idealLight) ? (cell.light / cell.idealLight) : 1;
        const baseLitersPerPercent = 2; // 2L needed per 1% deficit
        
        // Round to 1 d
        cell.waterNeeded = Math.round((moistureDeficit * baseLitersPerPercent * lightFactor) * 10) / 10;
    } else {
        cell.waterNeeded = 0;
    }

    if (score < 80)        { cell.status = 'dry';           cell.color = 'red'; }
    else if (score > 120)  { cell.status = 'oversaturated'; cell.color = 'blue'; }
    else                   { cell.status = 'optimal';       cell.color = 'green'; }
}

// GRID RENDER
function renderGrid() {
    document.querySelectorAll('.field-grid').forEach(grid => {
        grid.innerHTML = '';
        const isConfig = grid.closest('#tab-config') !== null;
        cells.forEach((cell, i) => {
            const el       = document.createElement('div');
            el.className   = isConfig ? 'field-cell status-unset' : `field-cell status-${cell.status}`;
            el.dataset.index = i;
            if (isConfig && selectedCells.has(i)) el.classList.add('is-selected');
            const cropInfo = cell.crop ? CROPS[cell.crop] : null;
            const cropText = cropInfo ? cropInfo.emoji + ' ' + cropInfo.label : cell.name;
            if (isConfig) {
                el.innerHTML = `<div class="cell-label"><div class="cell-crop">${cropText}</div><div class="cell-moisture" style="opacity:0.5">Select to edit</div></div>`;
                el.addEventListener('mousedown', e => { e.preventDefault(); startDrag(i); });
                el.addEventListener('mouseenter', () => { if (isDragging) extendDrag(i); });
                el.addEventListener('mouseup', endDrag);
                el.addEventListener('touchstart', e => { e.preventDefault(); startDrag(i); }, {passive: false});
                el.addEventListener('touchmove', e => {
                    e.preventDefault();
                    const t      = e.touches[0];
                    const target = document.elementFromPoint(t.clientX, t.clientY);
                    const cellEl = target?.closest('.field-cell');
                    if (cellEl?.dataset?.index) extendDrag(parseInt(cellEl.dataset.index));
                }, {passive: false});
                el.addEventListener('touchend', endDrag);
            } else {
                
                let moistureDisplay = '— unset';
                if (cell.moisture !== null) {
                    if (cell.waterNeeded > 0) {
                        moistureDisplay = `🚰 ${cell.waterNeeded}L needed`;
                    } else if (cell.status === 'oversaturated') {
                        moistureDisplay = `💧 Oversaturated`;
                    } else {
                        moistureDisplay = `✅ 0L needed`;
                    }
                }

                el.innerHTML = `
                    <div class="cell-status-dot"></div>
                    <div class="cell-label">
                        <div class="cell-crop">${cropText}</div>
                        <div class="cell-moisture">${moistureDisplay}</div>
                    </div>
                `;
            }
            grid.appendChild(el);
        });
    });
}

// ZONE SUMMARY PANEL
function renderStats() {
    const table = document.getElementById('zone-table');
    table.innerHTML = cells.map(cell=>{
        const dotColor  = cell.status==='optimal'?'#2ecc71':cell.status==='dry'?'#e74c3c':cell.status==='oversaturated'?'#3498db':'#aaa';
        const barColor  = dotColor;
        const scoreWidth = cell.score?Math.min(100,cell.score):0;
        const cropLabel = cell.crop?`${CROPS[cell.crop]?.emoji} ${CROPS[cell.crop]?.label}`:'—';
        
        // generate water requirement text if needed
        const waterText = cell.waterNeeded > 0 
            ? `<br><span style="color:#e74c3c;font-weight:600;display:inline-block;margin-top:4px;">🚰 ${cell.waterNeeded}L needed</span>` 
            : '';

        return `
            <div class="zone-row">
                <div class="zone-dot" style="background:${dotColor}"></div>
                <div class="zone-name">${cell.name}</div>
                <div class="zone-crop">${cropLabel}</div>
                <div class="score-bar-wrap"><div class="score-bar" style="width:${scoreWidth}%;background:${barColor}"></div></div>
                <div class="zone-score" style="color:${dotColor}">${cell.score!==null?cell.score+'%':'—'}</div>
                <div style="font-size:0.65rem;color:var(--muted);min-width:6rem;text-align:right">
                    ${cell.moisture!==null? '💧'+cell.moisture+'% ☀️'+cell.light:'no data'}
                    ${waterText}
                </div>
            </div>
        `;
    }).join('');
}
// ALERTS RENDER 
function renderAlerts() {
    const list   = document.getElementById('alerts-list');
    const alerts = [];
    
    cells.forEach(cell => {
        // Dry Alerts
        if(cell.status==='dry' && cell.crop){
            if(rainExpected) {
                alerts.push({icon:'🌧', text:`${cell.name} (${CROPS[cell.crop]?.label}) is dry — rain forecast, watering of ${cell.waterNeeded}L suppressed`, time:'Suppressed'});
            } else {
                alerts.push({icon:'🔴', text:`${cell.name} (${CROPS[cell.crop]?.label}) needs water! Moisture at ${cell.moisture}%. Apply approx ${cell.waterNeeded}L.`, time:'Now'});
            }
        }
        
        // Oversaturated Alerts
        if(cell.status==='oversaturated'){
            alerts.push({icon:'🔵', text:`${cell.name} oversaturated — risk of root rot. Moisture: ${cell.moisture}%`, time:'Now'});
        }

        // Bio-Alerts for Fungal Risk
        if(cell.crop === 'potatoes' && blightRisk) {
            alerts.push({
                icon: '🍄', 
                text: `Fungal Risk Warning: Warm & wet conditions coming. Inspect ${cell.name} leaves organically.`, 
                time: 'Next 24h'
            });
        }
    });

    list.innerHTML = alerts.length===0?'<div class="no-alerts">✅ No alerts — all zones nominal</div>':
        alerts.map(a=>`<div class="alert-item"><span class="alert-icon">${a.icon}</span><div><div class="alert-text">${a.text}</div><div class="alert-time">${a.time}</div></div></div>`).join('');
}

// DRAG SELECTION
function startDrag(i)  { isDragging=true; dragStart=i; selectedCells.clear(); selectedCells.add(i); renderGrid(); updateEditor(); }
function extendDrag(i) {
    if (!isDragging) return;
    const cols=3, r1=Math.floor(dragStart/cols), c1=dragStart%cols,
          r2=Math.floor(i/cols), c2=i%cols,
          minR=Math.min(r1,r2), maxR=Math.max(r1,r2),
          minC=Math.min(c1,c2), maxC=Math.max(c1,c2);
    selectedCells.clear();
    for (let r=minR; r<=maxR; r++) for (let c=minC; c<=maxC; c++) selectedCells.add(r*cols+c);
    renderGrid(); updateEditor();
}
function endDrag() { isDragging = false; }
document.addEventListener('mouseup', endDrag);

// CROP EDITOR
function updateEditor() {
    const editor   = document.getElementById('crop-editor');
    const prompt   = document.getElementById('editor-prompt');
    const selCount = document.getElementById('sel-count');
    if (selectedCells.size === 0) { editor.classList.remove('active'); selCount.textContent = ''; return; }
    editor.classList.add('active');
    selCount.textContent = `${selectedCells.size} zone${selectedCells.size>1?'s':''} selected`;
    prompt.textContent   = `Editing ${selectedCells.size} zone${selectedCells.size>1?'s':''}. Configure below and click Apply.`;
    const unique = [...new Set([...selectedCells].map(i => cells[i].crop).filter(Boolean))];
    if (unique.length === 1) { document.getElementById('crop-select').value = unique[0]; updateCropReq(); }
}
function updateCropReq() {
    const val = document.getElementById('crop-select').value;
    document.getElementById('crop-req').textContent = val ? CROP_REQ_TEXT[val] : 'Select a crop to see moisture & light requirements.';
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
    renderGrid(); renderStats(); renderAlerts();
    showToast(`✓ Applied ${CROPS[crop].label} to ${selectedCells.size} zone${selectedCells.size>1?'s':''}`);
    selectedCells.clear(); updateEditor();
}
function clearSelection() { selectedCells.clear(); renderGrid(); updateEditor(); }
document.getElementById('crop-select').addEventListener('change', updateCropReq);

// STATISTICS TAB
let chartInstance = null;

async function renderStatisticsTab() {
    // Show loading state
    ['stat-water-saved','stat-money-saved','stat-energy-saved','stat-optimal-pct']
        .forEach(id => document.getElementById(id).textContent = '…');

    let data;
    try {
        const resp = await fetch(`${STATS_URL}?days=${activePeriodDays}`);
        if (!resp.ok) throw new Error('Stats fetch failed');
        data = await resp.json();
    } catch(e) {
        showToast('Could not load statistics');
        ['stat-water-saved','stat-money-saved','stat-energy-saved','stat-optimal-pct']
            .forEach(id => document.getElementById(id).textContent = '—');
        return;
    }

    // KPI cards 
    const wl = data.total_water_saved_l;
    document.getElementById('stat-water-saved').textContent  = wl < 1000 ? Math.round(wl).toLocaleString() + ' L' : (wl/1000).toFixed(1) + ' kL';
    document.getElementById('stat-money-saved').textContent  = '£' + data.total_cost_saved_gbp.toFixed(2);
    document.getElementById('stat-energy-saved').textContent = data.total_energy_saved_kwh.toFixed(1) + ' kWh';
    document.getElementById('stat-optimal-pct').textContent  = data.overall_optimal_pct + '%';
    document.getElementById('stat-water-sub').textContent    = `over last ${activePeriodDays} day${activePeriodDays>1?'s':''}`;
    document.getElementById('stat-money-sub').textContent    = `water + pump energy over ${activePeriodDays}d`;
    document.getElementById('stat-energy-sub').textContent   = `pump runtime reduction over ${activePeriodDays}d`;

    // Chart 
    const canvas = document.getElementById('savings-chart');
    const empty  = document.getElementById('chart-empty');

    if (!data.daily_breakdown || data.daily_breakdown.length === 0) {
        canvas.style.display = 'none';
        empty.style.display  = 'flex';
    } else {
        canvas.style.display = 'block';
        empty.style.display  = 'none';

        const labels   = data.daily_breakdown.map(d => {
            const dt = new Date(d.date);
            return dt.toLocaleDateString('en-GB', { month: 'short', day: 'numeric' });
        });
        const baseline = data.daily_breakdown.map(d => d.baseline_l);
        const actual   = data.daily_breakdown.map(d => d.actual_l);
        const saved    = data.daily_breakdown.map(d => d.saved_l);

        if (chartInstance) {
            chartInstance.data.labels            = labels;
            chartInstance.data.datasets[0].data = baseline;
            chartInstance.data.datasets[1].data = actual;
            chartInstance.data.datasets[2].data = saved;
            chartInstance.update();
        } else {
            chartInstance = new Chart(canvas.getContext('2d'), {
                type: 'bar',
                data: {
                    labels,
                    datasets: [
                        { label: 'Baseline (L)', data: baseline, backgroundColor: 'rgba(160,192,216,0.6)', borderColor: '#7eb8d4', borderWidth: 1, borderRadius: 4 },
                        { label: 'Actual (L)',   data: actual,   backgroundColor: 'rgba(61,122,79,0.6)',   borderColor: '#3d7a4f', borderWidth: 1, borderRadius: 4 },
                        { label: 'Saved (L)',    data: saved,    backgroundColor: 'rgba(240,192,64,0.7)',  borderColor: '#f0c040', borderWidth: 1, borderRadius: 4, type: 'line', fill: false, tension: 0.35, pointRadius: 3 },
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false }, tooltip: { mode: 'index', intersect: false } },
                    scales: {
                        x: { grid: { display: false }, ticks: { font: { size: 11 } } },
                        y: { grid: { color: 'rgba(0,0,0,0.04)' }, ticks: { font: { size: 11 } }, title: { display: true, text: 'Litres', font: { size: 11 } } }
                    }
                }
            });
        }
    }

    // Zone efficiency table 
    const table = document.getElementById('zone-efficiency-table');
    if (!data.zone_breakdown || data.zone_breakdown.length === 0) {
        table.innerHTML = '<div style="color:var(--muted);font-size:0.85rem;padding:1rem 0">No zone data yet — keep the backend running to accumulate stats.</div>';
        return;
    }

    table.innerHTML = data.zone_breakdown.map(z => {
        const name      = PLOT_ID_TO_NAME[z.plot_id] || z.plot_id.slice(0,8);
        const idx       = ZONES_BACKEND[z.plot_id];
        const cell      = idx !== undefined ? cells[idx] : null;
        const cropInfo  = cell?.crop ? CROPS[cell.crop] : null;
        const cropLabel = cropInfo ? cropInfo.emoji + ' ' + cropInfo.label : '—';
        const eff       = z.efficiency_pct;
        const barColor  = eff >= 80 ? '#2ecc71' : eff >= 50 ? '#f0c040' : '#e74c3c';
        return `<div class="eff-row">
            <div class="eff-name">${name}</div>
            <div class="eff-crop">${cropLabel}</div>
            <div class="eff-bar-wrap"><div class="eff-bar" style="width:${eff}%;background:${barColor}"></div></div>
            <div class="eff-value" style="color:${barColor}">${eff}%</div>
            <div class="eff-saved">💧 ${Math.round(z.water_saved_l)} L saved</div>
        </div>`;
    }).join('');
}

// API READINGS 
async function fetchReadings() {
    try {
        const resp = await fetch(API_URL);
        if (!resp.ok) return;
        const data   = await resp.json();
        const latest = {};
        data.forEach(r => { if (!latest[r.plot_id]) latest[r.plot_id] = r; });
        Object.entries(latest).forEach(([plot_id, r]) => {
            const idx = ZONES_BACKEND[plot_id];
            if (idx === undefined) return;
            cells[idx].moisture = r.moisture;
            cells[idx].light    = r.light;
            if (!cells[idx].crop) { cells[idx].crop = 'wheat'; cells[idx].idealMoisture = 55; }
            recalcStatus(idx);
        });
        renderGrid(); renderStats(); renderAlerts();
        if (document.getElementById('tab-stats').classList.contains('active')) renderStatisticsTab();
    } catch(e) {}
}

// API WEATHER 
async function fetchWeather() {
    try {
        const resp = await fetch(`${BACKEND_WEATHER_BASE}/hourly?lat=${currentLocation.lat}&lon=${currentLocation.lon}`);
        if (!resp.ok) throw new Error();
        const data  = await resp.json();
        document.getElementById('location-label').textContent = data.location || 'UK';
        const strip = document.getElementById('weather-strip');
        strip.innerHTML = '';
        const now = new Date();
        data.hourly.forEach(h => {
            const t    = new Date(h.time);
            const pill = document.createElement('div');
            pill.className = 'hour-pill' + (Math.abs(t - now) < 3600000 ? ' current' : '');
            pill.innerHTML = `<span class="temp">${h.temp_c.toFixed(1)}°</span><span>${t.getHours()}:00</span><span class="rain">🌧${h.chance_of_rain}%</span>`;
            strip.appendChild(pill);
        });

        // Rain logic next 6 hours
        rainExpected = data.hourly.some(h => {
            const t = new Date(h.time);
            return t > now && t < new Date(+now + 6*3600000) && h.chance_of_rain > 60;
        });

        // Fungal/Blight logic check next 24 hours for warm & wet conditions
        blightRisk = data.hourly.some(h => {
            const t = new Date(h.time);
            return t > now && t < new Date(+now + 24*3600000) && h.temp_c >= 15 && h.chance_of_rain > 40;
        });

        const rainSoon = data.hourly.some(h => {
            const t = new Date(h.time);
            return t > now && t < new Date(+now + 6*3600000) && h.chance_of_rain > 20;
        });
        document.getElementById('rain-warning').textContent = rainSoon ? '🌧 Rain soon — no need to water!' : '';

        renderAlerts(); // ensures alerts update as soon as weather risk changes
    } catch(e) {
        console.error(e);
        showToast('Failed to fetch weather');
    }
}

// CITY SEARCH 
document.getElementById('location-input').addEventListener('keypress', async e => {
    if (e.key !== 'Enter') return;
    const query = e.target.value.trim();
    if (!query) return;
    try {
        const resp = await fetch(`${BACKEND_WEATHER_BASE}/search?query=${encodeURIComponent(query)}`);
        if (!resp.ok) throw new Error();
        const data = await resp.json();
        if (!data.length) { showToast('City not found'); return; }
        const { lat, lon, name, region, country } = data[0];
        currentLocation = { lat, lon };
        document.getElementById('location-label').textContent = `${name}, ${region ? region + ', ' : ''}${country}`;
        fetchWeather();
    } catch(e) { showToast('Failed to fetch location'); }
});

// TAB NAVIGATION 
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', e => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        e.target.classList.add('active');
        document.getElementById(e.target.dataset.target).classList.add('active');
        if (e.target.dataset.target === 'tab-stats') {
            if (chartInstance) { chartInstance.destroy(); chartInstance = null; }
            renderStatisticsTab();
        }
    });
});

// PERIOD FILTER
document.querySelectorAll('.period-btn').forEach(btn => {
    btn.addEventListener('click', e => {
        document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        activePeriodDays = parseInt(e.target.dataset.period);
        if (chartInstance) { chartInstance.destroy(); chartInstance = null; }
        renderStatisticsTab();
    });
});

// UTILITIES 
function updateClock() { document.getElementById('clock').textContent = new Date().toLocaleTimeString('en-GB'); }
function showToast(msg) { const t=document.getElementById('toast'); t.textContent=msg; t.classList.add('show'); setTimeout(()=>t.classList.remove('show'),2500); }

// INIT
renderGrid(); renderStats(); renderAlerts();
updateClock(); fetchWeather(); fetchReadings();
setInterval(fetchReadings, 5000);
setInterval(fetchWeather,  60000);
setInterval(updateClock,   1000);