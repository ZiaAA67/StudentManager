document.addEventListener("DOMContentLoaded", function() {
    // Lấy tất cả các link thông báo
    const notificationLinks = document.querySelectorAll('.notification-link');

    // Modal và các thành phần
    const modal = document.getElementById('notificationModal');
    const closeModal = document.getElementById('closeModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalContent = document.getElementById('modalContent');

    // Hiển thị modal khi người dùng click vào thông báo
    notificationLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const title = link.getAttribute('data-title');
            const content = link.getAttribute('data-content');

            // Cập nhật tiêu đề và nội dung trong modal
            modalTitle.textContent = title;
            modalContent.textContent = content;

            // Mở modal
            modal.style.display = 'block';
        });
    });

    // Đóng modal khi nhấn vào nút X
    closeModal.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    // Đóng modal nếu click ngoài modal
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});
