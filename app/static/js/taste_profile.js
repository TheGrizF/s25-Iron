// Initialize all ranking lists with Sortable
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.ranking-list').forEach(list => {
        new Sortable(list, {
            animation: 150,
            ghostClass: 'sortable-ghost'
        });
    });

    // Handle form submission
    document.getElementById('tasteProfileForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        // Mock user ID for prototype
        const mockUserId = "user123";

        // Get the flavor ranking list
        const flavorList = document.getElementById('flavorRanking');
        const flavorItems = Array.from(flavorList.children);
        
        // Find position of 'sweet' 
        const sweetPosition = flavorItems.findIndex(item => item.dataset.id === 'sweet');
        // Convert position to score (6 for first position, 1 for last position - because there are 6 options)
        const sweetScore = 6 - sweetPosition;

        // Mock taste scores for database 
        const mockTasteScores = {
            sweet: sweetScore, // Only sweet has been implemented, the rest are placeholders
            salty: 6,
            sour: 5,
            bitter: 4,
            umami: 8
        };

        // Gather all form data
        const tasteProfile = {
            userId: mockUserId,
            tasteScores: mockTasteScores,
            dietaryRestrictions: Array.from(document.querySelectorAll('input[name="allergens"]:checked, input[name="diets"]:checked'))
                .map(checkbox => checkbox.value)
                .concat(document.querySelector('input[name="otherAllergens"]').value)
                .filter(Boolean)
                .join(', ')
        };

        try {
            const response = await fetch('/api/taste-profile', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(tasteProfile)
            });

            if (response.ok) {
                alert('Taste profile saved successfully!');
                window.location.href = '/'; // Redirect to home page after success
            } else {
                throw new Error('Failed to save taste profile');
            }
        } catch (error) {
            console.error('Error saving taste profile:', error);
            alert('Failed to save taste profile. Please try again.');
        }
    });
}); 