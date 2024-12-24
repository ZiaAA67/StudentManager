document.getElementById('class-form').addEventListener('submit', function(e) {
    e.preventDefault();

    const className = document.querySelector('input[name="class_name"]').value;
    const grade = document.getElementById('grade').value;
    const alert = document.getElementById('alert');

    fetch("/api/classes",{
        method: "post",
        body: JSON.stringify({
            "class_name": className,
            "grade": grade
        }),
        headers: {
            "Content-Type": "application/json"
        }
    }).then(res => res.json()).then(data => {
        if(data.error) {
            alert.classList.add('alert-danger');
            alert.innerText = data.error;
        } else {
            location.reload();
        }
    })

})