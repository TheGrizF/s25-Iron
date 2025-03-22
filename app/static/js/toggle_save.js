function toggleSave(element, dishId) {
    let icon = element.querySelector("i");
    let isSaved = icon.classList.contains("saved");
    let text = element.querySelector("p");

    // Send AJAX request to Flask
    fetch("/toggle-save/" + dishId, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ saved: !isSaved }), // Toggle state
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Toggle icon classes based on new state

            if (isSaved) {
                icon.classList.remove("saved", "fas", "fa-bookmark");
                icon.classList.add("not-saved", "far", "fa-bookmark");

                if (text) {
                    text.classList.remove("saved");
                    text.textContent = "Save dish";
                } 
            }
            else {
            icon.classList.remove("not-saved", "far", "fa-bookmark");
            icon.classList.add("saved", "fas", "fa-bookmark");

                    if (text) {
                        text.classList.add("saved");
                        text.textContent = "Saved dish";
                }
            }
        }
    })
    .catch(error => console.error("Error:", error));
}