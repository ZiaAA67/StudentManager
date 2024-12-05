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


