const btnEdit = document.querySelector('.btn-edit');
const btnConfirm = document.querySelector('.btn-confirm');
const selectElement  = document.getElementById('cls');
const gradeData = document.getElementById('grade').dataset.grade;

btnEdit.addEventListener('click', (e) => {
    btnEdit.style.display = 'none';
    btnConfirm.style.display = 'block';
    selectElement.disabled = false;

    const selected = selectElement.value;

    fetch(`/get_classes/${gradeData}`)
            .then(response => response.json())
            .then(classes => {
                selectElement.innerHTML = `<option value="">Chọn lớp</option>`;
                classes.forEach(cls => {
                    const option = document.createElement('option');
                    option.value = cls.id;
                    option.textContent = cls.name;
                    if(cls.name === selected) {
                        option.selected = true;
                    }
                    selectElement.appendChild(option);
                });
            })
            .catch(error => console.error('Error', error));
})

btnConfirm.addEventListener('click', (e) => {
    btnEdit.style.display = 'block';
    btnConfirm.style.display = 'none';
    selectElement.disabled = true;

    const studentId = parseInt(document.getElementById('table').dataset.studentId);
    const classId = parseInt(selectElement.value);

    fetch('/change_class', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ classId, studentId })
    })
        .then(responsive => responsive.json())
        .then(data => {
            if (data.success) {
                alert("Thay đổi lớp thành công!");
            } else {
                alert("Có lỗi xảy ra!");
            }
        })
        .catch(e => console.log(e))
})