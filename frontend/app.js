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

// Submit report
async function submitReport(bin_id) {
    return api("/reports", { method: "POST", body: { bin_id, status: "full" } });
}

// Index page: handle form submission
function onIndexPage() {
    const form = document.getElementById("report-form");
    if (!form) return;

    const status = document.getElementById("status");
    const binInput = document.getElementById("bin-id"); // frontend input for bin_id

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        status.textContent = "Submitting...";
        try {
            const bin_id = binInput.value.trim();
            if (!bin_id) throw new Error("Bin ID is required");

            await submitReport(bin_id);

            status.textContent = "Report submitted. Thank you!";
            binInput.value = "";
            await refreshDashboard();
        } catch (err) {
            status.textContent = `Error: ${err.message || err}`;
        }
    });
}

// Load reports from backend
async function loadReports() {
    try {
        const reports = await api("/reports");
        return { reports };
    } catch (err) {
        console.error("Failed to fetch reports:", err);
        return { reports: [] };
    }
}

// Clear a single report
async function clearReport(reportId) {
    return api(`/reports/${reportId}/clear`, { method: "PUT" });
}

// Render table
function renderReportsTable(reports) {
    const tableBody = document.querySelector("#reports-table tbody");
    if (!tableBody) return;
    tableBody.innerHTML = "";

    if (!reports || reports.length === 0) {
        tableBody.innerHTML = "<tr><td colspan=6>No reports yet</td></tr>";
        return;
    }

    for (const r of reports) {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${r.id}</td>
            <td>${r.bin_id}</td>
            <td>${r.status}</td>
            <td>${new Date(r.created_at).toLocaleString()}</td>
            <td>${r.cleared_at ? new Date(r.cleared_at).toLocaleString() : "-"}</td>
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

// Map handling (optional)
let mapInstance = null;
let markersLayer = null;

function ensureMap() {
    const mapEl = document.getElementById("map");
    if (!mapEl) return null;
    if (!mapInstance) {
        mapInstance = L.map("map").setView([6.5244, 3.3792], 11);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap'
        }).addTo(mapInstance);
        markersLayer = L.layerGroup().addTo(mapInstance);
    }
    return mapInstance;
}

function renderMapMarkers(reports) {
    const map = ensureMap();
    if (!map || !markersLayer) return;
    markersLayer.clearLayers();

    for (const r of reports) {
        if (!r.latitude || !r.longitude) continue;
        const lat = parseFloat(r.latitude);
        const lng = parseFloat(r.longitude);
        if (isNaN(lat) || isNaN(lng)) continue;

        const htmlContent = r.status === "done" && r.cleared_at
            ? `<div class="marker-green">Done</div>`
            : `<div class="marker-red"></div>`;

        const binIcon = L.divIcon({ html: htmlContent, className: "", iconSize: [24, 24], iconAnchor: [12, 12] });
        const tooltipText = r.status === "done" && r.cleared_at
            ? `Bin ${r.bin_id} - Done at ${new Date(r.cleared_at).toLocaleString()}`
            : `Bin ${r.bin_id} - Full`;

        const marker = L.marker([lat, lng], { icon: binIcon });
        marker.bindTooltip(tooltipText, { permanent: false, direction: 'top', offset: [0, -10] });
        markersLayer.addLayer(marker);
    }
}

// Refresh dashboard
async function refreshDashboard() {
    const tableBody = document.querySelector("#reports-table tbody");
    if (tableBody) tableBody.innerHTML = "<tr><td colspan=6>Loading...</td></tr>";
    try {
        const { reports } = await loadReports();
        renderReportsTable(reports);
        renderMapMarkers(reports);
    } catch (err) {
        if (tableBody) tableBody.innerHTML = `<tr><td colspan=6>Error loading data: ${err.message || err}</td></tr>`;
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
