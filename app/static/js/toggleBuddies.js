let selectedBuddies = []; //list for Oronde to use

function toggleSuperBuddies() {
    const list = document.querySelector("#super-buddies .buddies-list");
    const chevron = document.querySelector("#super-buddies .buddies-header i");
    
    toggleSection(list, chevron);
}

function toggleTasteBuddies() {
    const list = document.querySelector("#taste-buddies .buddies-list");
    const chevron = document.querySelector("#taste-buddies .buddies-header i");
    
    toggleSection(list, chevron);
}

function toggleRegularBuddies() {
    const list = document.querySelector("#regular-buddies .buddies-list");
    const chevron = document.querySelector("#regular-buddies .buddies-header i");
    
    toggleSection(list, chevron);
}

function toggleSection(list, chevron) {
    if (list.style.display === 'none' || list.style.display === '') {
        list.style.display = 'block';
        chevron.className = 'fas fa-chevron-up';
    } else {
        list.style.display = 'none';
        chevron.className = 'fas fa-chevron-down';
    }
}

function toggleFollow(element) {
    let icon = element.querySelector("i");
    let userId = element.getAttribute("data-user-id");

    if (icon.classList.contains("bi-plus-circle")) {
        icon.classList.remove("bi-plus-circle");
        icon.classList.add("bi-plus-circle-fill");

        if (!selectedBuddies.includes(userId)) { //adds it to list for Oronde to use
            selectedBuddies.push(userId);
            console.log("Added user:", userId);
        }

    } else {
        icon.classList.remove("bi-plus-circle-fill");
        icon.classList.add("bi-plus-circle");
        selectedBuddies = selectedBuddies.filter(id => id !== userId);
        console.log("Removed user:", userId); // Confirm removal
    }
    console.log("Selected Buddies:", selectedBuddies); // Debugging
}

