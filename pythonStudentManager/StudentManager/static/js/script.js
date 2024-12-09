function togglePass(icon) {
    // Lấy phần tử input liên quan đến icon
    const inputField = icon.parentElement.querySelector('input');

    // Kiểm tra và thay đổi thuộc tính type của input (password <=> text)
    const type = inputField.type === 'password' ? 'text' : 'password';
    inputField.type = type;

    // Thay đổi emoji tùy theo trạng thái mật khẩu
    icon.innerHTML = type === 'password' ? '🙉' : '🙈'; // 🙉 ẩn mật khẩu, 🙈 hiển thị mật khẩu
}


function goToRegisterPage() {
    window.location.href = "/register";  // Chuyển hướng đến route "register"
}

function goToLoginPage() {
    window.location.href = "/login";  // Chuyển hướng đến route "register"
}

function checkPasswordStrength() {
    const password = document.getElementById('password').value;
    const strengthBar = document.getElementById('strength-bar');
    const strengthText = document.getElementById('strength-text');

    let strength = 0;

    // Tiêu chí kiểm tra mật khẩu
    if (password.length >= 8) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[@$!%*?&]/.test(password)) strength++;

    // Cập nhật thanh và text dựa trên độ mạnh
    switch (strength) {
        case 0:
        case 1:
            strengthBar.style.width = "20%";
            strengthBar.style.backgroundColor = "red";
            strengthText.innerText = "Rất yếu";
            break;
        case 2:
            strengthBar.style.width = "40%";
            strengthBar.style.backgroundColor = "orange";
            strengthText.innerText = "Yếu";
            break;
        case 3:
            strengthBar.style.width = "60%";
            strengthBar.style.backgroundColor = "yellow";
            strengthText.innerText = "Trung bình";
            break;
        case 4:
            strengthBar.style.width = "80%";
            strengthBar.style.backgroundColor = "blue";
            strengthText.innerText = "Mạnh";
            break;
        case 5:
            strengthBar.style.width = "100%";
            strengthBar.style.backgroundColor = "green";
            strengthText.innerText = "Rất mạnh";
            break;
    }
}

function validateConfirmPassword() {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    const confirmFeedback = document.getElementById('confirm-password-feedback');

    if (confirmPassword === "") {
        confirmFeedback.innerText = "Vui lòng nhập xác nhận mật khẩu.";
        confirmFeedback.style.color = "red";
        return false;
    } else if (confirmPassword !== password) {
        confirmFeedback.innerText = "Mật khẩu xác nhận không khớp.";
        confirmFeedback.style.color = "red";
        return false;
    } else {
        confirmFeedback.innerText = "Mật khẩu khớp!";
        confirmFeedback.style.color = "green";
        return true;
    }
}
function validateForm(event) {
    if (!validateConfirmPassword()) {
        event.preventDefault(); // Ngăn form submit nếu xác nhận mật khẩu sai
    }
}

function previewAvatar() {
        const file = document.getElementById('avatar').files[0];
        const preview = document.getElementById('avatarPreview');

        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        } else {
            preview.style.display = 'none';
        }
    }







