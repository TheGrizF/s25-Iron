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
    let firstName = element.getAttribute("data-first-name");
    let lastName = element.getAttribute("data-last-name");
    let iconPath = element.getAttribute("data-icon-path");

    if (icon.classList.contains("bi-plus-circle")) {
        icon.classList.remove("bi-plus-circle");
        icon.classList.add("bi-plus-circle-fill");

        if (!selectedBuddies.some(buddy => buddy.userId === userId)) { // Prevent duplicates
            selectedBuddies.push({ userId, firstName, lastName, iconPath });
            console.log("Added user:", userId);
            updateBuddyDisplay();
        }

    } else {
        icon.classList.remove("bi-plus-circle-fill");
        icon.classList.add("bi-plus-circle");

        selectedBuddies = selectedBuddies.filter(buddy => buddy.userId !== userId);
        console.log("Removed user:", userId);
        updateBuddyDisplay();
    }

    console.log("Selected Buddies:", selectedBuddies); // Debugging
}


function updateBuddyDisplay() {
    const buddyList = document.querySelector('.group-match-buddies-list');
    if (!buddyList) {
        console.error('group-match-buddies-list not found!');
        return;
    }

    buddyList.innerHTML = '';

    selectedBuddies.forEach(buddy => {
        if (!buddy) {
            console.error("Invalid buddy data:", buddy);
            return;
        }

        //const iconSrc = buddy.iconPath || "/static/images/profile_icons/default1.png";
        let iconSrc = buddy.iconPath ? `/static/${buddy.iconPath}` : "/static/images/profile_icons/default1.png";
        const buddyElement = document.createElement('div');
        buddyElement.classList.add('buddy');
        buddyElement.innerHTML = `
            <img src="${iconSrc}" alt="Buddy Icon">
            <span>${buddy.firstName} ${buddy.lastName}</span>
        `;
        buddyList.appendChild(buddyElement);
    });
}

/*function updateBuddyDisplay() {
    const buddyList = document.querySelector('.group-match-buddies-list');
    if (!buddyList) {
        console.error('group-match-buddies-list not found!');
        return;
    }

    buddyList.innerHTML = '';

    selectedBuddies.forEach(buddy => {
        if (!buddy) {
            console.error("Invalid buddy data:", buddy);
            return;
        }

        let iconSrc = buddy.iconPath ? `/static/${buddy.iconPath}` : "/static/images/profile_icons/default1.png";
        const buddyElement = document.createElement('div');
        buddyElement.classList.add('group-buddy');
        buddyElement.setAttribute('data-user-id', buddy.userId);
        buddyElement.setAttribute('data-first-name', buddy.firstName);
        buddyElement.setAttribute('data-last-name', buddy.lastName);
        buddyElement.setAttribute('data-icon-path', buddy.iconPath);
        buddyElement.innerHTML = `
            <img src="${iconSrc}" alt="${buddy.firstName} ${buddy.lastName}" class="group-buddy-icon" />
            <span class="group-buddy-name">${buddy.firstName} ${buddy.lastName}</span>
            <i class="bi bi-x-circle remove-buddy" onclick="removeBuddy(${buddy.userId})"></i>
        `;
        buddyList.appendChild(buddyElement);
    });
}*/

function removeBuddy(userId) {
    selectedBuddies = selectedBuddies.filter(buddy => buddy.userId !== userId.toString());
    updateBuddyDisplay();
    
    // Update the plus/minus icon in the original list
    const buddyElement = document.querySelector(`.follow-btn[data-user-id="${userId}"]`);
    if (buddyElement) {
        const icon = buddyElement.querySelector('i');
        icon.classList.remove('bi-plus-circle-fill');
        icon.classList.add('bi-plus-circle');
    }
}
