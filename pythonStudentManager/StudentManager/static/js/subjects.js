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


//add class
document.getElementById('subject-form').addEventListener('submit', function (e) {
    e.preventDefault();

    const subjectName = document.querySelector('input[name="class_name"]').value;
    const desc = document.getElementById('description').value;
    const grade = document.getElementById('grade').value;

    fetch("/api/subjects", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "subject_name": subjectName,
            "desc": desc,
            "grade": grade
        })
    }).then(res => res.json()).then(data => {
        if(data.success) {
            location.reload()
            const totalSubject = document.getElementById('pagination').getAttribute('page-data')
            if(totalSubject%4 === 0) {
                window.location.href = `/subjects?page=${(parseInt(totalSubject)/4)+1}`;
            }
        } else {
            location.reload()
        }
    })

})


//delete class
function deleteClass(subjectId) {
    fetch(`/api/subjects/delete/${subjectId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({})
    }).then(response => response.json()).then(data => {
        if (data.success) {
            location.reload();
            const totalSubject = document.getElementById('pagination').getAttribute('page-data')
            if(totalSubject%4 === 1) {
                window.location.href = `/subjects?page=${(parseInt(totalSubject)-1)/4}`;
            }
        } else {
            location.reload();
        }
    })
}