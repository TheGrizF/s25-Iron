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
    
    if (dietaryForm) {
        dietaryForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const allergens = Array.from(document.querySelectorAll('input[name="allergens"]:checked'))
                .map(cb => cb.value);
            const diets = Array.from(document.querySelectorAll('input[name="diets"]:checked'))
                .map(cb => cb.value);
            
            const formData = {
                allergens: allergens,
                otherAllergy: document.getElementById('otherAllergy').value,
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
                    window.location.href = '/taste-profile/step9';  // Changed from /profile to next step
                } else {
                    throw new Error('Failed to save bitter preference');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to save preference. Please try again.');
            }
        });
    }

    if (document.getElementById('atmospherePreferenceForm')) {
        document.getElementById('atmospherePreferenceForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const selectedValue = document.querySelector('input[name="atmospherePreference"]:checked').value;
            
            try {
                const response = await fetch('/api/taste-profile/step9', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ atmosphere: selectedValue })
                });

                if (response.ok) {
                    window.location.href = '/taste-profile/step10';  // Changed from /profile to next step
                } else {
                    throw new Error('Failed to save atmosphere preference');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to save preference. Please try again.');
            }
        });
    }

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
                italian: parseInt(document.getElementById('italian').value),
                japanese: parseInt(document.getElementById('japanese').value),
                french: parseInt(document.getElementById('french').value),
                american: parseInt(document.getElementById('american').value),
                spanish: parseInt(document.getElementById('spanish').value),
                mexican: parseInt(document.getElementById('mexican').value)
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
                    window.location.href = '/taste-profile/step11';  // Changed from /profile to next step
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