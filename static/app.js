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
    wrapper.innerHTML = `${label} <input id="${id}" type="range" min="0" max="1" step="0.01" value="${value}" />`;
    root.appendChild(wrapper);
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
  if (!results.length) {
    root.textContent = "No districts matched your constraints.";
    return;
  }
  root.innerHTML = results
    .map(
      (district) =>
        `<article class="district-card"><strong>${district.district_name}, ${district.state}</strong><br/>Score: ${district.score}</article>`
    )
    .join("");
}

async function runSearch() {
  const query = readParams();
  const response = await fetch(`/districts?${query.toString()}`);
  const payload = await response.json();
  renderResults(payload.results);
}

renderWeightInputs();
document.getElementById("search_btn").addEventListener("click", runSearch);
runSearch();
