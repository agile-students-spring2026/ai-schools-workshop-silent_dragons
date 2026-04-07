const WEIGHT_FIELDS = [
  ["academics_weight", "Academics", 0.25],
  ["safety_weight", "Safety", 0.2],
  ["affordability_weight", "Affordability", 0.15],
  ["diversity_weight", "Diversity", 0.1],
  ["special_ed_weight", "Special Ed", 0.15],
  ["teacher_support_weight", "Teacher Support", 0.1],
  ["class_size_weight", "Class Size", 0.05],
];

function renderWeightInputs() {
  const root = document.getElementById("weights");
  WEIGHT_FIELDS.forEach(([id, label, value]) => {
    const wrapper = document.createElement("label");
    wrapper.className = "weight-row";
    wrapper.innerHTML = `
      <div class="weight-label-row">
        <span>${label}</span>
        <span class="weight-value" id="${id}_value">${Number(value).toFixed(2)}</span>
      </div>
      <input id="${id}" type="range" min="0" max="1" step="0.01" value="${value}" />
    `;
    root.appendChild(wrapper);

    const input = document.getElementById(id);
    input.addEventListener("input", () => {
      document.getElementById(`${id}_value`).textContent = Number(input.value).toFixed(2);
    });
  });
}

function readParams() {
  const params = new URLSearchParams();
  params.set("top_k", document.getElementById("top_k").value);
  params.set("min_grad_rate", document.getElementById("min_grad_rate").value);
  params.set(
    "max_student_teacher_ratio",
    document.getElementById("max_student_teacher_ratio").value
  );
  WEIGHT_FIELDS.forEach(([id]) => params.set(id, document.getElementById(id).value));
  return params;
}

function renderResults(results) {
  const root = document.getElementById("results");
  document.getElementById("results_count").textContent = `${results.length} districts`;
  if (!results.length) {
    root.innerHTML = `<p class="status">No districts matched your constraints.</p>`;
    return;
  }
  root.innerHTML = results
    .map(
      (district) =>
        `<article class="district-card">
          <div class="district-title">
            <span>${district.district_name}</span>
            <span>${district.state}</span>
          </div>
          <div class="district-meta">District ID: ${district.district_id}</div>
          <div class="score-row">
            <span class="score-pill">${district.score}</span>
            <div class="score-bar"><div class="score-fill" style="width:${district.score}%"></div></div>
          </div>
        </article>`
    )
    .join("");
}

async function runSearch() {
  const root = document.getElementById("results");
  root.innerHTML = `<p class="status">Loading districts...</p>`;
  const query = readParams();
  try {
    const response = await fetch(`/districts?${query.toString()}`);
    if (!response.ok) {
      throw new Error("Request failed");
    }
    const payload = await response.json();
    renderResults(payload.results);
  } catch (_error) {
    root.innerHTML = `<p class="status">Unable to load results. Please try again.</p>`;
  }
}

renderWeightInputs();
document.getElementById("search_btn").addEventListener("click", runSearch);
runSearch();
