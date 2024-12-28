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
            } else {
                localStorage.setItem('studentInfo', JSON.stringify(formData))
                location.reload()
            }
        })
});



//delete class
function deleteStudent(studentId) {
    fetch(`/api/students/delete/${studentId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({})
    }).then(response => response.json()).then(data => {
        if (data.success) {
            location.reload();
            // const totalClasses = document.getElementById('pagination').getAttribute('page-data')
            // if(totalClasses%4 === 1) {
            //     window.location.href = `/classes?page=${(parseInt(totalClasses)-1)/4}`;
            // }
        } else {
            location.reload();
        }
    })
}
