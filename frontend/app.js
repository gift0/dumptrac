// ✅ Backend URL
const BASE_URL =
  window.location.hostname.includes("localhost") || window.location.hostname.includes("127.0.0.1")
    ? "http://127.0.0.1:8000/api"
    : "https://dumptrac.vercel.app/api";

// Generic API helper with JSON parsing
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

// ------------------ INDEX PAGE ------------------
async function ensureBin(location, latitude, longitude) {
  if (latitude == null || longitude == null) {
    throw new Error("Latitude and longitude are required.");
  }
  return api("/bins", {
    method: "POST",
    body: { location, latitude, longitude }
  });
}

async function submitReport(location, latitude, longitude) {
  const bin = await ensureBin(location, latitude, longitude);
  return api("/reports", {
    method: "POST",
    body: { bin_id: bin.id, status: "full" }
  });
}

function onIndexPage() {
  const form = document.getElementById("report-form");
  if (!form) return;

  const status = document.getElementById("status");
  const useLocationBtn = document.getElementById("use-location");
  const geoStatus = document.getElementById("geo-status");
  const latEl = document.getElementById("lat");
  const lngEl = document.getElementById("lng");
  const locationInput = document.getElementById("location");

  useLocationBtn?.addEventListener("click", () => {
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

    const location = locationInput.value.trim();
    const lat = parseFloat(latEl.value);
    const lng = parseFloat(lngEl.value);

    if (!location) {
      status.textContent = "Error: Location description is required.";
      return;
    }
    if (isNaN(lat) || isNaN(lng)) {
      status.textContent = "Error: Please attach your coordinates using 'Use My Location'.";
      return;
    }

    try {
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

// ------------------ DASHBOARD PAGE ------------------
async function loadReports() {
  try {
    return { reports: await api("/reports") };
  } catch (err) {
    console.error("Failed to fetch reports:", err);
    return { reports: [] };
  }
}

async function clearReport(reportId) {
  return api(`/reports/${reportId}/clear`, { method: "PUT" });
}

function renderReportsTable(reports) {
  const tableBody = document.querySelector("#reports-table tbody");
  if (!tableBody) return;
  tableBody.innerHTML = "";

  if (!reports.length) {
    tableBody.innerHTML = "<tr><td colspan=8>No reports yet</td></tr>";
    return;
  }

  for (const r of reports) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${r.id}</td>
      <td>${r.bin_id}</td>
      <td>${r.bin?.location || "-"}</td>
      <td>${r.bin?.latitude || "-"}</td>
      <td>${r.bin?.longitude || "-"}</td>
      <td>${r.status === "done" ? "Done" : "Full"}</td>
      <td>${new Date(r.created_at).toLocaleString()}</td>
      <td>
        ${r.status !== "done" ? `<button class="clear-btn" data-id="${r.id}">Clear</button>` : "-"}
      </td>
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

// ------------------ MAP ------------------
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
    if (!r.bin?.latitude || !r.bin?.longitude) continue;
    const lat = parseFloat(r.bin.latitude);
    const lng = parseFloat(r.bin.longitude);
    if (isNaN(lat) || isNaN(lng)) continue;

    // ✅ Circle markers instead of icons
    let markerCircle;
    if (r.status === "done") {
      markerCircle = L.circleMarker([lat, lng], {
        radius: 10,
        color: "green",
        fillColor: "green",
        fillOpacity: 0.9
      });
    } else {
      markerCircle = L.circleMarker([lat, lng], {
        radius: 10,
        color: "red",
        fillColor: "red",
        fillOpacity: 0.9,
        className: "blinking-marker" // CSS handles glow/blink
      });
    }

    const tooltipText =
      r.status === "done"
        ? `${r.bin.location} - Done at ${new Date(r.cleared_at).toLocaleString()}`
        : `${r.bin.location} - Full`;

    markerCircle.bindTooltip(tooltipText, { permanent: false, direction: 'top', offset: [0, -10] });
    markersLayer.addLayer(markerCircle);
  }
}

// Refresh dashboard
async function refreshDashboard() {
  const tableBody = document.querySelector("#reports-table tbody");
  if (tableBody) tableBody.innerHTML = "<tr><td colspan=8>Loading...</td></tr>";
  try {
    const { reports } = await loadReports();
    renderReportsTable(reports);
    renderMapMarkers(reports);
  } catch (err) {
    if (tableBody) tableBody.innerHTML = `<tr><td colspan=8>Error loading data: ${err.message || err}</td></tr>`;
    console.error(err);
  }
}

// Dashboard initialization
function onDashboardPage() {
  const refreshBtn = document.getElementById("refresh");
  if (!refreshBtn) return;
  refreshBtn.addEventListener("click", refreshDashboard);
  refreshDashboard();
}

// ------------------ INIT ------------------
window.addEventListener("DOMContentLoaded", () => {
  onIndexPage();
  onDashboardPage();
});
