function districtIdFromPath() {
  const parts = window.location.pathname.split("/").filter(Boolean);
  return parts[1] || "";
}

const urlParams = new URLSearchParams(window.location.search);
let selectedAudience = urlParams.get("audience") === "educator" ? "educator" : "parent";

function syncAudienceButtons() {
  const buttons = [...document.querySelectorAll(".lens-btn")];
  buttons.forEach((button) => {
    button.classList.toggle("active", button.dataset.audience === selectedAudience);
  });
}

function metricValue(metric) {
  if (metric.value === null || metric.value === undefined) {
    return "Not available";
  }
  if (metric.unit === "$") {
    return `$${Number(metric.value).toLocaleString()}`;
  }
  return `${metric.value}${metric.unit || ""}`;
}

function metricCard(metric) {
  return `
    <article class="result-card">
      <h4>${metric.label}</h4>
      <p class="metric-value">${metricValue(metric)}</p>
      <p class="card-meta">Source: ${metric.source_name} (${metric.source_year}) • ${metric.level}</p>
    </article>
  `;
}

function schoolCard(school) {
  return `
    <article class="result-card">
      <div class="card-title-row">
        <h4><a href="/school/${school.school_id}?audience=${selectedAudience}">${school.school_name}</a></h4>
        <span class="pill">${school.school_type}</span>
      </div>
      <p class="card-subtitle">Grade span: ${school.grade_span} • Enrollment: ${school.enrollment ?? "N/A"}</p>
      <p class="card-meta">${school.charter_status} • Flags: ${school.quick_flags.join(" • ")}</p>
    </article>
  `;
}

async function loadDistrict() {
  const districtId = districtIdFromPath();
  history.replaceState({}, "", `/district/${districtId}?audience=${selectedAudience}`);
  document.querySelector(".back-link").href = `/?audience=${selectedAudience}`;
  const gradeBand = document.getElementById("grade_band_filter").value;
  const schoolType = document.getElementById("school_type_filter").value;
  const params = new URLSearchParams({
    audience: selectedAudience,
    grade_band: gradeBand,
    school_type: schoolType,
  });

  const metricsRoot = document.getElementById("district_metrics");
  const schoolsRoot = document.getElementById("schools_list");
  metricsRoot.innerHTML = `<p class="status">Loading district metrics...</p>`;
  schoolsRoot.innerHTML = `<p class="status">Loading schools...</p>`;

  try {
    const response = await fetch(`/districts/${districtId}/overview?${params.toString()}`);
    if (!response.ok) {
      throw new Error("Unable to load district");
    }
    const payload = await response.json();

    document.getElementById("district_title").textContent = payload.district_name;
    document.getElementById("district_subtitle").textContent = `${payload.state} • ${payload.locale}`;
    document.getElementById("summary_parent").textContent = payload.summary.parent;
    document.getElementById("summary_educator").textContent = payload.summary.educator;
    document.getElementById("summary_parent_mode").textContent = payload.audience_differences.parent;
    document.getElementById("summary_educator_mode").textContent = payload.audience_differences.educator;
    document.getElementById("lens_objective").textContent = payload.audience_objective;
    document.getElementById("metric_count").textContent = `${payload.metrics.length} metrics`;
    syncAudienceButtons();

    metricsRoot.innerHTML = payload.metrics.map(metricCard).join("");

    const mapEmbed = payload.map_preview.embed_url
      ? `<iframe
          title="District map preview"
          class="map-frame"
          src="${payload.map_preview.embed_url}"
          loading="lazy"
        ></iframe>`
      : `<p class="status">Map coordinates are not available for this district yet.</p>`;

    document.getElementById("map_preview").innerHTML = `
      <p><strong>${payload.map_preview.title}</strong></p>
      <p class="card-summary">${payload.map_preview.description}</p>
      ${mapEmbed}
      <p class="card-meta">Focus communities: ${payload.map_preview.focus_cities.join(", ") || "Not available"}</p>
      <p class="card-meta">Source: ${payload.map_preview.source_name}${payload.map_preview.source_year ? ` (${payload.map_preview.source_year})` : ""}</p>
    `;

    document.getElementById("schools_count").textContent = `${payload.schools.length} schools shown`;
    schoolsRoot.innerHTML = payload.schools.length
      ? payload.schools.map(schoolCard).join("")
      : `<p class="status">No schools match the selected filters.</p>`;
  } catch (_error) {
    metricsRoot.innerHTML = `<p class="status">Unable to load district overview right now.</p>`;
    schoolsRoot.innerHTML = "";
  }
}

document.getElementById("grade_band_filter").addEventListener("change", loadDistrict);
document.getElementById("school_type_filter").addEventListener("change", loadDistrict);
document.getElementById("district_lens_parent").addEventListener("click", () => {
  selectedAudience = "parent";
  loadDistrict();
});
document.getElementById("district_lens_educator").addEventListener("click", () => {
  selectedAudience = "educator";
  loadDistrict();
});
loadDistrict();
