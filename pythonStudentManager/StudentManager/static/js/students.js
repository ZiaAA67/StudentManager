document.getElementById('student-form').addEventListener('submit', function (event) {
    event.preventDefault();

    var formData = {
        name: document.getElementById('name').value,
        gender: document.querySelector('input[name="gender"]:checked').value,
        date_of_birth: document.getElementById('date_of_birth').value,
        address: document.getElementById('address').value,
        phone: document.getElementById('phone').value,
        email: document.getElementById('email').value,
        grade: document.getElementById('grade').value
    };

    fetch('/api/students', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('error-message').innerText = data.error;
                document.getElementById('error-message').style.display = 'block';
            } else {
                document.getElementById('student-form').reset();
                document.getElementById('error-message').style.display = 'none';

                var successMessage = document.createElement('div');
                successMessage.classList.add('alert', 'alert-success');
                successMessage.innerText = 'Thông tin học sinh đã được lưu thành công!';
                document.getElementById('student-form').appendChild(successMessage);

                setTimeout(function () {
                    successMessage.style.display = 'none';
                }, 5000);
            }
        })
        .catch((error) => {
            console.error('Lỗi:', error);
            document.getElementById('error-message').innerText = 'Đã xảy ra lỗi, vui lòng thử lại!';
            document.getElementById('error-message').style.display = 'block';
        });
});
