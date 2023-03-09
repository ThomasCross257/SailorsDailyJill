// Add event listener to password field
var passwordField = document.getElementById("password-field");
passwordField.addEventListener("input", function() {
    var complexityScore = calculatePasswordComplexity(this.value);
    updatePasswordComplexityDisplay(complexityScore);
    updateSubmitButton(complexityScore);
});

function calculatePasswordComplexity(password) {
    // Calculate complexity score
    var complexity = 0;
    if (password.length >= 8) {
        complexity += 1;
    }
    if (/[A-Z]/.test(password)) {
        complexity += 1;
    }
    if (/[a-z]/.test(password)) {
        complexity += 1;
    }
    if (/\d/.test(password)) {
        complexity += 1;
    }
    if (/[\W_]/.test(password)) {
        complexity += 1;
    }
    return complexity;
}

function updatePasswordComplexityDisplay(complexityScore) {
    // Update DOM with complexity score
    var complexityDisplay = document.getElementById("password-complexity");
    complexityDisplay.innerText = "Password complexity: " + complexityScore;
    if (complexityScore < 3) {
        complexityDisplay.style.color = "red";
    } else if (complexityScore < 5) {
        complexityDisplay.style.color = "orange";
    } else {
        complexityDisplay.style.color = "green";
    }
}

function updateSubmitButton(complexityScore) {
    // Disable or enable submit button based on complexity score
    var submitButton = document.getElementById("submit-button");
    if (complexityScore < 3) {
        submitButton.disabled = true;
    } else {
        submitButton.disabled = false;
    }
}
