document.addEventListener("DOMContentLoaded", function() {
    const generatePasswordButton = document.getElementById("generate-password-button");
    generatePasswordButton.addEventListener("click", function() {
        const passwordField = document.getElementById("id_password");
        passwordField.value = generateRandomPassword();
    });

    function generateRandomPassword() {
        const characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
        let password = "";
        for (let i = 0; i < 12; i++) {
            const randomIndex = Math.floor(Math.random() * characters.length);
            password += characters.charAt(randomIndex);
        }
        return password;
    }
});