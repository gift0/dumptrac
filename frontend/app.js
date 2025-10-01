// ✅ Backend URL
const BASE_URL =
    window.location.hostname.includes("localhost") || window.location.hostname.includes("127.0.0.1")
        ? "http://127.0.0.1:8000/api"
        : "https://dumptrac.vercel.app/api";

// Generic API helper
async function api(path, options = {}) {
    const res = await fetch(`${BASE_URL}${path}`, {
        method: options.method || "GET",
        headers: { "Content-Type": "application/json", ...(options.headers || {}) },
        body: options.body ? JSON.stringify(options.body) : undefined,
    });
    if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Request failed: ${res.status}`);
    }
    return res.json();
}

// Ensure bin exists
async function ensureBin(location, latitude, longitude) {
    return api("/bins", { 
        method: "POST", 
        body: { location: String(location), latitude: String(latitude), longitude: String(longitude) } 
    });
}

// Submit report
async function submitReport(location, latitude, longitude) {
    const bin = await ensureBin(location, latitude, longitude);
    return api("/reports", { method: "POST", body: { bin_id: bin.id, status: "full" } });
}

// Index page: handle form submission
function onIndexPage() {
    const form = document.getElementById("report-form");
    if (!form) return;

    const status = document.getElementById("status");
    const useLocationBtn = document.getElementById("use-location");
    const geoStatus = document.getElementById("geo-status");
    const latEl = document.getElementById("lat");
    const lngEl = document.getElementById("lng");

    useLocationBtn?.addEventListener("click", async () => {
        geoStatus.textContent = "Fetching location...";
        if (!navigator.geolocation) {
            geoStatus.textContent = "Geolocation not supported";
            return;
        }
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const { latitude, longitude } = pos.coords;
                latEl.value = latitude.toFixed(6);
                lngEl.value = longitude.toFixed(6);
                geoStatus.textContent = `Attached coords: ${latitude.toFixed(5)}, ${longitude.toFixed(5)}`;
            },
            (err) => { geoStatus.textContent = `Location error: ${err.message}`; },
            { enableHighAccuracy: true, timeout: 10000 }
        );
    });

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        status.textContent = "Submitting...";
        const locationInput = document.getElementById("location");
        const lat = parseFloat(latEl.value);
        const lng = parseFloat(lngEl.value);

        if (isNaN(lat) || isNaN(lng)) {
            status.textContent = "Error: Please attach your current location before submitting.";
            return;
        }

        try {
            const location = locationInput.value.trim();
            if (!location) throw new Error("Location is required");

            await submitReport(location, lat, lng);

            status.textContent = "Report submitted. Thank you!";
            locationInput.value = "";
            latEl.value = "";
            lngEl.value = "";
            geoStatus.textContent = "";
            await refreshDashboard();
        } catch (err) {
            status.textContent = `Error: ${err.message || err}`;
        }
    });
}

// Load reports and bins
async function loadReports() {
    const [reports, bins] = await Promise.all([api("/reports"), api("/bins")]);
    const binIdToBin = new Map(bins.map(b => [b.id, b]));
    return { reports, binIdToBin };
}

// Clear a single report
async function clearReport(reportId) {
    return api(`/reports/${reportId}/clear`, { method: "PUT" });
}

// Render table with Clear button
function renderReportsTable(reports, binIdToBin) {
    const tableBody = document.querySelector("#reports-table tbody");
    if (!tableBody) return;
    tableBody.innerHTML = "";

    if (reports.length === 0) {
        tableBody.innerHTML = "<tr><td colspan=8>No reports yet</td></tr>";
        return;
    }

    for (const r of reports) {
        const b = binIdToBin.get(r.bin_id) || {};
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${r.id}</td>
            <td>${r.bin_id}</td>
            <td>${b.location || "-"}</td>
            <td>${b.latitude ?? "-"}</td>
            <td>${b.longitude ?? "-"}</td>
            <td>${r.status}</td>
            <td>${new Date(r.created_at).toLocaleString()}</td>
            <td>${r.status !== 'done' ? `<button class="clear-btn" data-id="${r.id}">Clear</button>` : "-"}</td>
        `;
        tableBody.appendChild(tr);
    }

    document.querySelectorAll(".clear-btn").forEach(btn => {
        btn.addEventListener("click", async (e) => {
            const id = e.target.dataset.id;
            try {
                await clearReport(id);
                await refreshDashboard();
            } catch (err) {
                alert(`Error clearing report: ${err.message || err}`);
            }
        });
    });
}

// Map handling
let mapInstance = null;
let markersLayer = null;

function ensureMap() {
    const mapEl = document.getElementById("map");
    if (!mapEl) return null;
    if (!mapInstance) {
        mapInstance = L.map("map").setView([6.5244, 3.3792], 11); // Lagos
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap'
        }).addTo(mapInstance);
        markersLayer = L.layerGroup().addTo(mapInstance);
    }
    return mapInstance;
}

// Render map markers
function renderMapMarkers(reports, binIdToBin) {
    const map = ensureMap();
    if (!map || !markersLayer) return;
    markersLayer.clearLayers();

    for (const r of reports) {
        const b = binIdToBin.get(r.bin_id);
        if (!b) continue;
        const lat = parseFloat(b.latitude);
        const lng = parseFloat(b.longitude);
        if (isNaN(lat) || isNaN(lng)) continue;

        const htmlContent = r.status === "done" && r.cleared_at
            ? `<div class="marker-green">Done</div>`
            : `<div class="marker-red"></div>`;

        const binIcon = L.divIcon({ html: htmlContent, className: "", iconSize: [24, 24], iconAnchor: [12, 12] });
        const tooltipText = r.status === "done" && r.cleared_at
            ? `${b.location || 'Unknown'} - Done at ${new Date(r.cleared_at).toLocaleString()}`
            : `${b.location || 'Unknown'} - Bin Full`;

        const marker = L.marker([lat, lng], { icon: binIcon });
        marker.bindTooltip(tooltipText, { permanent: false, direction: 'top', offset: [0, -10] });
        markersLayer.addLayer(marker);
    }
}

// Refresh dashboard
async function refreshDashboard() {
    const tableBody = document.querySelector("#reports-table tbody");
    if (tableBody) tableBody.innerHTML = "<tr><td colspan=8>Loading...</td></tr>";
    try {
        const { reports, binIdToBin } = await loadReports();
        renderReportsTable(reports, binIdToBin);
        renderMapMarkers(reports, binIdToBin);
    } catch (err) {
        if (tableBody) tableBody.innerHTML = `<tr><td colspan=8>Error loading data: ${err.message || err}</td></tr>`;
        console.error(err);
    }
}

// Dashboard page initialization
function onDashboardPage() {
    const refreshBtn = document.getElementById("refresh");
    if (!refreshBtn) return;
    refreshBtn.addEventListener("click", refreshDashboard);
    refreshDashboard();
}

// Init
window.addEventListener("DOMContentLoaded", () => {
    onIndexPage();
    onDashboardPage();
});
