let selectedAudience = "parent";

function renderResults(payload) {
  const root = document.getElementById("results");

  const districtCount = payload.districts.length;
  const schoolCount = payload.schools.length;
  const suggestionCount = payload.district_suggestions.length;

  document.getElementById("results_count").textContent =
    `${districtCount} district matches • ${schoolCount} school matches`;
  document.getElementById("helper_text").textContent = payload.helper_text;

  if (!districtCount && !schoolCount && !suggestionCount) {
    root.innerHTML =
      `<p class="status">No matches yet. Try a ZIP code, a city, or a full district/school name.</p>`;
    return;
  }

  const suggestionMarkup = suggestionCount
    ? `
      <section class="results-group">
        <h3>Likely districts for this ZIP</h3>
        <p class="group-help">ZIP matches are estimates, not guaranteed assignments.</p>
        ${payload.district_suggestions
          .map(
            (item) => `
              <article class="result-card suggestion-card">
                <div class="card-title-row">
                  <h4><a href="/district/${item.district_id}">${item.district_name}</a></h4>
                  <span class="pill">Likely #${item.likelihood_rank}</span>
                </div>
                <p class="card-subtitle">${item.state} • ${item.district_id}</p>
                <p class="card-summary">${item.why_it_matches}</p>
                <p class="card-meta">Source: ${item.source_name}${item.source_year ? ` (${item.source_year})` : ""}</p>
              </article>
            `
          )
          .join("")}
      </section>
    `
    : "";

  const districtMarkup = districtCount
    ? `
      <section class="results-group">
        <h3>Matching districts</h3>
        ${payload.districts
          .map(
            (district) => `
              <article class="result-card">
                <div class="card-title-row">
                  <h4><a href="/district/${district.district_id}">${district.title}</a></h4>
                  <span class="pill">District</span>
                </div>
                <p class="card-subtitle">${district.subtitle}</p>
                <p class="card-summary">${district.summary}</p>
                <p class="card-meta">Coming soon: ${district.plain_language_metrics.join(" • ")}</p>
              </article>
            `
          )
          .join("")}
      </section>
    `
    : `
      <section class="results-group">
        <h3>Matching districts</h3>
        <p class="status">No district matches for this search yet.</p>
      </section>
    `;

  const schoolMarkup = schoolCount
    ? `
      <section class="results-group">
        <h3>Matching schools</h3>
        ${payload.schools
          .map(
            (school) => `
              <article class="result-card">
                <div class="card-title-row">
                  <h4><a href="/school/${school.school_id}">${school.title}</a></h4>
                  <span class="pill">School</span>
                </div>
                <p class="card-subtitle">${school.subtitle}</p>
                <p class="card-summary">${school.summary}</p>
                <p class="card-meta">District: ${school.district_name}</p>
              </article>
            `
          )
          .join("")}
      </section>
    `
    : `
      <section class="results-group">
        <h3>Matching schools</h3>
        <p class="status">No school matches for this search yet.</p>
      </section>
    `;

  root.innerHTML = `${suggestionMarkup}${districtMarkup}${schoolMarkup}`;
}

async function runSearch() {
  const query = document.getElementById("query").value.trim();
  const root = document.getElementById("results");
  if (!query) {
    root.innerHTML = `<p class="status">Please enter a ZIP, city, district, or school name.</p>`;
    document.getElementById("results_count").textContent = "No search yet";
    return;
  }

  root.innerHTML = `<p class="status">Searching districts and schools...</p>`;
  try {
    const params = new URLSearchParams({ query, audience: selectedAudience });
    const response = await fetch(`/search?${params.toString()}`);
    if (!response.ok) {
      throw new Error("Request failed");
    }
    const payload = await response.json();
    renderResults(payload);
  } catch (_error) {
    root.innerHTML = `<p class="status">Unable to load results right now. Please try again.</p>`;
  }
}

function wireAudienceButtons() {
  const buttons = [...document.querySelectorAll(".audience-btn")];
  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      selectedAudience = button.dataset.audience;
      buttons.forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      document.getElementById("helper_text").textContent =
        selectedAudience === "parent"
          ? "Parent mode selected. Search by ZIP, city, district, or school."
          : "Educator mode selected. Search by ZIP, city, district, or school.";
    });
  });
}

wireAudienceButtons();
document.getElementById("search_btn").addEventListener("click", runSearch);
document.getElementById("query").addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    runSearch();
  }
});
