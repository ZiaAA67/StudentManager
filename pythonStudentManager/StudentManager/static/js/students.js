const ipName = document.getElementById('name');
const ipBirth = document.getElementById('date_of_birth');
const ipAddress = document.getElementById('address');
const ipPhone = document.getElementById('phone');
const ipEmail = document.getElementById('email');
const ipGrade = document.getElementById('grade') ;


// show message
window.onload = function() {
    const flashMessages = document.getElementById("flash-messages");
    if (flashMessages) {
        flashMessages.style.display = "block";
        setTimeout(function() {
            flashMessages.style.display = "none";
        }, 5000);
    }
};

if(localStorage.getItem('studentInfo')) {
    const info = JSON.parse(localStorage.getItem('studentInfo'))
    ipName.value = info.name;

    const gender = document.getElementsByName('gender');
    for(const g of gender) {
        if(g.value === info.gender) {
            g.checked = true;
        }
    }

    ipBirth.value = info.date_of_birth
    ipAddress.value = info.address;
    ipPhone.value = info.phone;
    ipEmail.value = info.email;
    ipGrade.value = info.grade;

    localStorage.clear()
}


document.getElementById('student-form').addEventListener('submit', function (event) {
    event.preventDefault();

    const formData = {
        name: ipName.value,
        gender: document.querySelector('input[name="gender"]:checked').value,
        date_of_birth: ipBirth.value,
        address: ipAddress.value,
        phone: ipPhone.value,
        email: ipEmail.value,
        grade: ipGrade.value
    };

    console.log(formData)

    fetch('/api/students', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
        .then(response => response.json())
        .then(data => {

            if(data.success) {
                location.reload()
                // const totalClasses = document.getElementById('pagination').getAttribute('page-data')
                // if(totalClasses%4 === 0) {
                //     window.location.href = `/classes?page=${(parseInt(totalClasses)/4)+1}`;
                // }
            } else {
                localStorage.setItem('studentInfo', JSON.stringify(formData))
                location.reload()
            }

            // if (data.error) {
            //     document.getElementById('error-message').innerText = data.error;
            //     document.getElementById('error-message').style.display = 'block';
            // } else {
            //     document.getElementById('student-form').reset();
            //     document.getElementById('error-message').style.display = 'none';
            //
            //     var successMessage = document.createElement('div');
            //     successMessage.classList.add('alert', 'alert-success');
            //     successMessage.innerText = 'Thông tin học sinh đã được lưu thành công!';
            //     document.getElementById('student-form').appendChild(successMessage);
            //
            //     setTimeout(function () {
            //         successMessage.style.display = 'none';
            //     }, 5000);
            // }
        })
        // .catch((error) => {
        //     console.error('Lỗi:', error);
        //     document.getElementById('error-message').innerText = 'Đã xảy ra lỗi, vui lòng thử lại!';
        //     document.getElementById('error-message').style.display = 'block';
        // });
});
