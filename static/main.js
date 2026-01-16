const input = document.getElementById("drugInput");
const suggestionsBox = document.getElementById("suggestions");
const selectedDrugsBox = document.getElementById("selectedDrugs");

let selectedDrugs = [];

/* ---------------- AUTOCOMPLETE ---------------- */
input.addEventListener("input", () => {
  const value = input.value.trim();
  if (value.length < 2) {
    suggestionsBox.classList.add("hidden");
    return;
  }

  fetch(`/autocomplete?q=${value}`)
    .then(res => res.json())
    .then(data => {
      suggestionsBox.innerHTML = "";
      data.forEach(drug => {
        const div = document.createElement("div");
        div.className = "px-4 py-2 hover:bg-gray-100 cursor-pointer text-sm";
        div.innerText = drug;
        div.onclick = () => addDrug(drug);
        suggestionsBox.appendChild(div);
      });
      suggestionsBox.classList.remove("hidden");
    });
});

/* ---------------- ADD DRUG ---------------- */
function addDrug(drug) {
  if (selectedDrugs.includes(drug)) return;

  selectedDrugs.push(drug);
  renderDrugs();
  input.value = "";
  suggestionsBox.classList.add("hidden");
}

/* ---------------- REMOVE DRUG ---------------- */
function removeDrug(drug) {
  selectedDrugs = selectedDrugs.filter(d => d !== drug);
  renderDrugs();
}

/* ---------------- RENDER TAGS ---------------- */
function renderDrugs() {
  selectedDrugsBox.innerHTML = "";
  selectedDrugs.forEach(drug => {
    const tag = document.createElement("div");
    tag.className =
      "flex items-center gap-2 bg-gray-100 border rounded-full px-4 py-1 text-sm";

    tag.innerHTML = `
      ${drug}
      <button onclick="removeDrug('${drug}')"
        class="text-pink-500 font-bold">−</button>
    `;
    selectedDrugsBox.appendChild(tag);
  });
}

/* ---------------- SUBMIT ---------------- */
function submitDrugs() {
  if (selectedDrugs.length < 2) {
    alert("Please select at least two medicines.");
    return;
  }

  fetch("/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      medicines: selectedDrugs.join(",")
    })
  })
  .then(res => res.json())
  .then(showResults);
}

/* ---------------- CLEAR ---------------- */
function clearAll() {
  selectedDrugs = [];
  renderDrugs();
  document.getElementById("results").innerHTML = "";
}

/* ---------------- RESULTS ---------------- */
function showResults(data) {
  let html = "";

  data.forEach(r => {
    let effectsHtml = "";

    r.side_effects.forEach(e => {
      let color =
        e.severity === "severe" ? "text-red-600" :
        e.severity === "moderate" ? "text-yellow-600" :
        "text-green-600";

      effectsHtml += `
        <div class="text-sm mt-1">
          <span class="${color} font-semibold">${e.name}</span>
          <span class="text-gray-600"> – ${e.explanation}</span>
        </div>
      `;
    });

    html += `
      <div class="bg-white border rounded-lg p-4 mb-4 shadow">
        <div class="font-semibold text-lg">${r.pair}</div>

        <div class="mt-2">
          Severity:
          <span class="font-bold">${r.severity}</span>
        </div>

        <div class="mt-1">
          Risk Score: ${r.risk_score}/100
        </div>

        <div class="mt-3">
          <div class="font-semibold">Possible Side Effects:</div>
          ${effectsHtml || "<div class='text-sm text-gray-500'>No known side effects found.</div>"}
        </div>
      </div>
    `;
  });

  document.getElementById("results").innerHTML = html;
}
