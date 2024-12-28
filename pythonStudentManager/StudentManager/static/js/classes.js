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
document.getElementById('class-form').addEventListener('submit', function (e) {
    e.preventDefault();

    const className = document.querySelector('input[name="class_name"]').value;
    const grade = document.getElementById('grade').value;

    fetch("/api/classes", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "class_name": className,
            "grade": grade,
        })
    }).then(res => res.json()).then(data => {
        if(data.success) {
            // location.reload()
            const totalClasses = document.getElementById('pagination').getAttribute('page-data')
            if(totalClasses%4 === 0) {
                window.location.href = `/classes?page=${(parseInt(totalClasses)/4)+1}`;
            }
        } else {
            location.reload()
        }
    })

})


//delete class
function deleteClass(classId) {
    fetch(`/api/classes/delete/${classId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({})
    }).then(response => response.json()).then(data => {
        if (data.success) {
            location.reload();
            const totalClasses = document.getElementById('pagination').getAttribute('page-data')
            if(totalClasses%4 === 1 && ((parseInt(totalClasses)-1)/4) > 0) {
                window.location.href = `/classes?page=${(parseInt(totalClasses)-1)/4}`;
            }
        } else {
            location.reload();
        }
    })
}