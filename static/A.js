// A.js

document.addEventListener('DOMContentLoaded', function() {
    
    // --- 1. Form Submission Feedback ---
    // This function prevents double-clicks on login/register buttons and gives users visual feedback
    // that the server is processing their request.

    const submitButtons = document.querySelectorAll('button[type="submit"]');

    submitButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            
            // Check if the button is inside a form
            const form = button.closest('form');
            
            // Basic check to ensure the browser considers the form valid before disabling the button
            if (form && form.checkValidity()) {
                
                // Change the button appearance and disable it
                button.disabled = true;
                
                // Add a simple loading indicator
                button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
            }
            // If the form is invalid (e.g., missing required fields), the browser will handle the error message
            // and the button remains enabled.
        });
    });

    // --- 2. Product Card Interaction (For the Dashboard/Sneakers Page) ---
    // A placeholder to make the product cards feel more interactive.
    
    const productCards = document.querySelectorAll('.product-card');
    
    productCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            // Add a style class when the mouse is over the card
            card.style.boxShadow = '0 6px 15px rgba(0, 0, 0, 0.25)';
        });

        card.addEventListener('mouseleave', function() {
            // Restore the original shadow when the mouse leaves
            card.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
        });
        
        // You could add a click event here to navigate to a detail page later:
        // card.addEventListener('click', function() {
        //     window.location.href = '/product/ID'; 
        // });
    });

});