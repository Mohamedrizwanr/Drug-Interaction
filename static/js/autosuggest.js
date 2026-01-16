const input = document.getElementById("drug-input");
const suggestionBox = document.getElementById("suggestions");

input.addEventListener("keyup", async () => {
    const value = input.value.split(",").pop().trim();

    if (value.length < 3) {
        suggestionBox.classList.add("hidden");
        return;
    }

    const response = await fetch(`/autocomplete?q=${value}`);
    const suggestions = await response.json();

    suggestionBox.innerHTML = "";

    if (suggestions.length === 0) {
        suggestionBox.classList.add("hidden");
        return;
    }

    suggestions.forEach(name => {
        const li = document.createElement("li");
        li.textContent = name;
        li.className = "p-2 hover:bg-blue-100 cursor-pointer";

        li.onclick = () => {
            let parts = input.value.split(",");
            parts.pop();
            parts.push(" " + name);
            input.value = parts.join(",").trim() + ", ";
            suggestionBox.classList.add("hidden");
        };

        suggestionBox.appendChild(li);
    });

    suggestionBox.classList.remove("hidden");
});
