function schoolIdFromPath() {
  const parts = window.location.pathname.split("/").filter(Boolean);
  return parts[1] || "";
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

function qaCard(title, payload) {
  return `
    <article class="result-card">
      <h3>${title}</h3>
      <p class="card-summary">${payload.answer}</p>
      <p class="card-meta">Citations: ${payload.citations.join(", ")}</p>
    </article>
  `;
}

async function loadSchool() {
  const schoolId = schoolIdFromPath();
  const metricsRoot = document.getElementById("school_metrics");
  metricsRoot.innerHTML = `<p class="status">Loading school metrics...</p>`;

  try {
    const response = await fetch(`/schools/${schoolId}/detail`);
    if (!response.ok) {
      throw new Error("Unable to load school");
    }
    const payload = await response.json();

    document.getElementById("school_title").textContent = payload.school_name;
    document.getElementById("school_subtitle").textContent =
      `${payload.city}, ${payload.state} • ${payload.school_type} • Grades ${payload.grade_span}`;
    document.getElementById("fit_parent").textContent = payload.fit_explanations.parent;
    document.getElementById("fit_educator").textContent = payload.fit_explanations.educator;

    metricsRoot.innerHTML = payload.metrics.map(metricCard).join("");

    document.getElementById("district_context").innerHTML = `
      <p><strong>${payload.district_context.district_name}</strong></p>
      <p class="card-summary">Poverty context: ${payload.district_context.poverty_context}%</p>
      <p class="card-summary">Per-pupil spending: $${payload.district_context.per_pupil_spending.toLocaleString()}</p>
      <p class="card-summary">Graduation rate: ${payload.district_context.graduation_rate}%</p>
      <p class="card-meta">District-level context from structured district metrics.</p>
    `;

    document.getElementById("qa_panel").innerHTML = [
      qaCard("What stands out here?", payload.qa.what_stands_out),
      qaCard("What concerns should I notice?", payload.qa.what_concerns),
      qaCard("How does this school compare with the district?", payload.qa.compare_to_district),
    ].join("");

    document.getElementById("missing_notes").textContent = payload.missing_notes.length
      ? payload.missing_notes.join(" ")
      : "No missing data notes.";
    document.getElementById("district_back_link").href = `/district/${payload.district_id}`;
  } catch (_error) {
    metricsRoot.innerHTML = `<p class="status">Unable to load school detail right now.</p>`;
  }
}

loadSchool();
