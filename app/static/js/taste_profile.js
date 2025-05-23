// Initialize all ranking lists with Sortable
document.addEventListener('DOMContentLoaded', function() {
    // Remove or comment out these debug logs
    // console.log('Script loaded');
    
    document.querySelectorAll('.ranking-list').forEach(list => {
        new Sortable(list, {
            animation: 150,
            ghostClass: 'sortable-ghost'
        });
    });

    // Get the form
    const tasteProfileForm = document.getElementById('tasteProfileForm');
    
    // Only add event listener if form exists
    if (tasteProfileForm) {
        tasteProfileForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Get form data
            const formData = {
                favoriteRestaurant: document.getElementById('favoriteRestaurant').value,
                favoriteDish: document.getElementById('favoriteDish').value,
                tryNew: document.querySelector('input[name="tryNew"]:checked').value
            };
            
            console.log('Sending form data:', formData); // Debug log
            
            try {
                const response = await fetch('/api/taste-profile/step1', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                const responseData = await response.json();
                console.log('Server response:', responseData); // Debug log

                if (response.ok) {
                    window.location.href = '/taste-profile/step2';
                } else {
                    throw new Error('Failed to save taste profile step 1');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to save preferences. Please try again.');
            }
        });
    }

    const dietaryForm = document.getElementById('dietaryForm');
    const otherAllergyInput = document.getElementById('otherAllergy');
    const addOtherAllergyButton = document.getElementById('addOtherAllergy');
    const otherAllergyList = document.getElementById('otherAllergyList');
    let otherAllergies = [];

    if (addOtherAllergyButton && otherAllergyInput && otherAllergyList) {
        addOtherAllergyButton.addEventListener('click', () => {
            const allergy = otherAllergyInput.value.trim();
            if (allergy) {
                otherAllergies.push(allergy);
                const allergyItem = document.createElement('div');
                allergyItem.textContent = allergy;
                otherAllergyList.appendChild(allergyItem);
                otherAllergyInput.value = '';
            }
        });
    }

    if (dietaryForm) {
        dietaryForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const allergens = Array.from(document.querySelectorAll('input[name="allergens"]:checked'))
                .map(cb => cb.value);
            const diets = Array.from(document.querySelectorAll('input[name="diets"]:checked'))
                .map(cb => cb.value);
            
            const formData = {
                allergens: allergens,
                otherAllergies: otherAllergies, // Update this line
                diets: diets
            };

            try {
                const response = await fetch('/api/taste-profile/step2', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                if (response.ok) {
                    window.location.href = '/taste-profile/step3';  // Next step or completion page
                } else {
                    throw new Error('Failed to save dietary preferences');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to save preferences. Please try again.');
            }
        });
    }

    if (document.getElementById('sourPreferenceForm')) {
        document.getElementById('sourPreferenceForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const selectedValue = document.querySelector('input[name="sourPreference"]:checked').value;
            
            try {
                const response = await fetch('/api/taste-profile/step3', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ sour: parseInt(selectedValue) })
                });

                if (response.ok) {
                    window.location.href = '/taste-profile/step4';  // For the next step
                } else {
                    throw new Error('Failed to save sour preference');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to save preference. Please try again.');
            }
        });
    }

    if (document.getElementById('sweetPreferenceForm')) {
        document.getElementById('sweetPreferenceForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const selectedValue = document.querySelector('input[name="sweetPreference"]:checked').value;
            
            try {
                const response = await fetch('/api/taste-profile/step4', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ sweet: parseInt(selectedValue) })
                });

                if (response.ok) {
                    window.location.href = '/taste-profile/step5';  // For the next step
                } else {
                    throw new Error('Failed to save sweet preference');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to save preference. Please try again.');
            }
        });
    }

    if (document.getElementById('umamiPreferenceForm')) {
        document.getElementById('umamiPreferenceForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const selectedValue = document.querySelector('input[name="umamiPreference"]:checked').value;
            
            try {
                const response = await fetch('/api/taste-profile/step5', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ umami: parseInt(selectedValue) })
                });

                if (response.ok) {
                    window.location.href = '/taste-profile/step6';  // For the next step
                } else {
                    throw new Error('Failed to save umami preference');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to save preference. Please try again.');
            }
        });
    }

    if (document.getElementById('savoryPreferenceForm')) {
        document.getElementById('savoryPreferenceForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const selectedValue = document.querySelector('input[name="savoryPreference"]:checked').value;
            
            try {
                const response = await fetch('/api/taste-profile/step6', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ savory: parseInt(selectedValue) })
                });

                if (response.ok) {
                    window.location.href = '/taste-profile/step7';  // For the next step
                } else {
                    throw new Error('Failed to save savory preference');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to save preference. Please try again.');
            }
        });
    }

    if (document.getElementById('spicyPreferenceForm')) {
        document.getElementById('spicyPreferenceForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const selectedValue = document.querySelector('input[name="spicyPreference"]:checked').value;
            
            try {
                const response = await fetch('/api/taste-profile/step7', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ spicy: parseInt(selectedValue) })
                });

                if (response.ok) {
                    window.location.href = '/taste-profile/step8';  // For the next step
                } else {
                    throw new Error('Failed to save spicy preference');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to save preference. Please try again.');
            }
        });
    }

    if (document.getElementById('bitterPreferenceForm')) {
        document.getElementById('bitterPreferenceForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const selectedValue = document.querySelector('input[name="bitterPreference"]:checked').value;
            
            try {
                const response = await fetch('/api/taste-profile/step8', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ bitter: parseInt(selectedValue) })
                });

                if (response.ok) {
                    window.location.href = '/taste-profile/step10';  // Changed from step9 to step10
                } else {
                    throw new Error('Failed to save bitter preference');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to save preference. Please try again.');
            }
        });
    }

    // if (document.getElementById('atmospherePreferenceForm')) {
    //     document.getElementById('atmospherePreferenceForm').addEventListener('submit', async (e) => {
    //         ... entire block ...
    //     });
    // }

    if (document.getElementById('cuisinePreferenceForm')) {
        // Update slider values in real-time
        document.querySelectorAll('.preference-slider').forEach(slider => {
            slider.addEventListener('input', function() {
                document.getElementById(this.id + 'Value').textContent = this.value;
            });
        });

        document.getElementById('cuisinePreferenceForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const cuisinePreferences = {
                asian: parseInt(document.getElementById('asian').value),
                american: parseInt(document.getElementById('american').value),
                sushi: parseInt(document.getElementById('sushi').value),
                thai: parseInt(document.getElementById('thai').value),
                indian: parseInt(document.getElementById('indian').value),
                southern: parseInt(document.getElementById('southern').value),
                italian: parseInt(document.getElementById('italian').value),
                mexican: parseInt(document.getElementById('mexican').value),
                healthy: parseInt(document.getElementById('healthy').value),
                mediterranean: parseInt(document.getElementById('mediterranean').value)
            };
            
            try {
                const response = await fetch('/api/taste-profile/step10', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ cuisines: cuisinePreferences })
                });

                if (response.ok) {
                    window.location.href = '/taste-profile/step11';
                } else {
                    throw new Error('Failed to save cuisine preferences');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to save preferences. Please try again.');
            }
        });
    }

    if (document.getElementById('condimentPreferenceForm')) {
        document.getElementById('condimentPreferenceForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const selectedCondiments = Array.from(document.querySelectorAll('input[name="condiments"]:checked'))
                .map(checkbox => checkbox.value);
            
            try {
                const response = await fetch('/api/taste-profile/step11', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ condiments: selectedCondiments })
                });

                if (response.ok) {
                    window.location.href = '/taste-profile/debug';  // Redirect to debug page
                } else {
                    throw new Error('Failed to save condiment preferences');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to save preferences. Please try again.');
            }
        });
    }
});

// Add this function after the DOMContentLoaded event listener
async function submitBasicProfile() {
    const favoriteRestaurant = document.getElementById('favoriteRestaurant').value;
    const favoriteDish = document.getElementById('favoriteDish').value;
    const tryNewElement = document.querySelector('input[name="tryNew"]:checked');
    
    if (!favoriteRestaurant || !favoriteDish || !tryNewElement) {
        alert('Please fill in all required fields');
        return;
    }

    const formData = {
        favoriteRestaurant,
        favoriteDish,
        tryNew: tryNewElement.value,
        basicProfileOnly: true
    };
    
    try {
        const response = await fetch('/api/taste-profile/step1', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            window.location.href = '/profile';
        } else {
            throw new Error('Failed to save basic profile');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to save preferences. Please try again.');
    }
}

async function submitStep(step, data, done = false) {
    try {
        const response = await fetch(`/api/taste-profile/step${step}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`Failed to save taste profile step ${step}`);
        }

        if (done) {
            const doneDone = await fetch('/api/taste-profile/exit_early',
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!doneDone.ok) throw new Error('Failed to save and exit');
            window.location.href = '/profile';
        } else { 
            const nextStep = step === 8 ? 10 : step + 1;
            window.location.href = `/taste-profile/step${nextStep}`;
        }

    } catch (error) {
        console.error('Error:', error);
        alert('Failed to save preferences. Please try again.');
    }
}

function addOtherAllergy() {
    const otherAllergyInput = document.getElementById('otherAllergy');
    const otherAllergyList = document.getElementById('otherAllergyList');
    
    const allergy = otherAllergyInput.value.trim();
    if (allergy) {
        const allergyItem = document.createElement('div');
        allergyItem.className = 'other-allergy-item';
        allergyItem.textContent = allergy;
        otherAllergyList.appendChild(allergyItem);
        otherAllergyInput.value = '';
    }
}