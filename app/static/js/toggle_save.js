function toggleSave(element, dishId) {
    let icon = element.querySelector("i");
    let isSaved = icon.classList.contains("saved");

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
            } else {
                icon.classList.remove("not-saved", "far", "fa-bookmark");
                icon.classList.add("saved", "fas", "fa-bookmark");
            }
        }
    })
    .catch(error => console.error("Error:", error));
}