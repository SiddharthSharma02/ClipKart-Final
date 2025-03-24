document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality
    const tabBtns = document.querySelectorAll('.tab-btn');
    const forms = document.querySelectorAll('.auth-form');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all buttons and forms
            tabBtns.forEach(b => b.classList.remove('active'));
            forms.forEach(f => f.classList.remove('active'));
            
            // Add active class to clicked button and corresponding form
            this.classList.add('active');
            const formId = this.getAttribute('data-target');
            document.getElementById(formId).classList.add('active');
        });
    });
    
    // Login form submission
    const loginBtn = document.getElementById('login-btn');
    loginBtn.addEventListener('click', function() {
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        
        // Basic validation
        if (!email || !password) {
            showFormError('login-form', 'Please fill in all fields');
            return;
        }
        
        // For demo purposes, redirect to home page
        // In a real app, this would validate credentials with the server
        redirectToHome();
    });
    
    // Sign-up form submission
    const signupBtn = document.getElementById('signup-btn');
    signupBtn.addEventListener('click', function() {
        const name = document.getElementById('signup-name').value;
        const email = document.getElementById('signup-email').value;
        const password = document.getElementById('signup-password').value;
        const confirm = document.getElementById('signup-confirm').value;
        
        // Basic validation
        if (!name || !email || !password || !confirm) {
            showFormError('signup-form', 'Please fill in all fields');
            return;
        }
        
        if (password !== confirm) {
            showFormError('signup-form', 'Passwords do not match');
            return;
        }
        
        // For demo purposes, redirect to home page
        // In a real app, this would create an account on the server
        redirectToHome();
    });
    
    // Helper function to show form errors
    function showFormError(formId, message) {
        const form = document.getElementById(formId);
        
        // Remove any existing error
        const existingError = form.querySelector('.form-error');
        if (existingError) {
            existingError.remove();
        }
        
        // Create and insert error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'form-error';
        errorDiv.textContent = message;
        
        // Insert error above the submit button
        const submitBtn = form.querySelector('.auth-btn');
        form.insertBefore(errorDiv, submitBtn);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    }
    
    // Helper function to redirect to home page
    function redirectToHome() {
        window.location.href = '/home';
    }
    
    // Add Enter key support for forms
    document.getElementById('login-password').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            loginBtn.click();
        }
    });
    
    document.getElementById('signup-confirm').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            signupBtn.click();
        }
    });
    
    // Add error styling to login.css
    const style = document.createElement('style');
    style.textContent = `
        .form-error {
            background-color: rgba(255, 59, 48, 0.1);
            border-left: 3px solid var(--error);
            color: var(--error);
            padding: 0.75rem;
            margin-bottom: 1rem;
            border-radius: 4px;
            font-size: 0.9rem;
            animation: fadeIn 0.3s ease-out;
        }
    `;
    document.head.appendChild(style);
}); 