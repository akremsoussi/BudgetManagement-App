document.addEventListener('DOMContentLoaded', function() {
    const togglePassword = document.getElementById('togglePassword');
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirm_password');
    const passwordStrength = document.getElementById('passwordStrength');
    const passwordMatch = document.getElementById('passwordMatch');
    const submitBtn = document.getElementById('submitBtn');

    togglePassword.addEventListener('click', function() {
        const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
        password.setAttribute('type', type);
        this.querySelector('i').classList.toggle('fa-eye');
        this.querySelector('i').classList.toggle('fa-eye-slash');
    });

    confirmPassword.addEventListener('input', checkPasswordMatch);
    password.addEventListener('input', function() {
        checkPasswordStrength();
        if (confirmPassword.value) {
            checkPasswordMatch();
        }
    });

    function checkPasswordMatch() {
        if (password.value === confirmPassword.value) {
            passwordMatch.textContent = 'Les mots de passe correspondent.';
            passwordMatch.className = 'form-text text-success';
            confirmPassword.classList.remove('is-invalid');
            confirmPassword.classList.add('is-valid');
        } else {
            passwordMatch.textContent = 'Les mots de passe ne correspondent pas.';
            passwordMatch.className = 'form-text text-danger';
            confirmPassword.classList.remove('is-valid');
            confirmPassword.classList.add('is-invalid');
        }
        validateForm();
    }

    function checkPasswordStrength() {
        const value = password.value;
        let strength = 0;

        if (value.length >= 8) strength += 1;
        if (/[A-Z]/.test(value)) strength += 1;
        if (/[a-z]/.test(value)) strength += 1;
        if (/[0-9]/.test(value)) strength += 1;
        if (/[^A-Za-z0-9]/.test(value)) strength += 1;

        let message = '';
        let className = '';

        if (value.length === 0) {
            message = '';
            className = '';
            password.classList.remove('is-valid', 'is-invalid');
        } else if (strength < 3) {
            message = 'Mot de passe faible';
            className = 'form-text text-danger';
            password.classList.remove('is-valid');
            password.classList.add('is-invalid');
        } else if (strength < 5) {
            message = 'Mot de passe moyen';
            className = 'form-text text-warning';
            password.classList.remove('is-invalid', 'is-valid');
        } else {
            message = 'Mot de passe fort';
            className = 'form-text text-success';
            password.classList.remove('is-invalid');
            password.classList.add('is-valid');
        }

        passwordStrength.textContent = message;
        passwordStrength.className = className;
        validateForm();
    }

    function validateForm() {
        const isPasswordValid = password.value.length >= 8;
        const isPasswordMatch = password.value === confirmPassword.value;
        submitBtn.disabled = !(isPasswordValid && (confirmPassword.value === '' || isPasswordMatch));
    }
});
