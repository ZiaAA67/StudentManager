const gradeElement = document.getElementById('grade');
const classElement = document.getElementById('class');
const subjectElement = document.getElementById('subject');
const semesterElement = document.getElementById('semester');

const btnConfirm = document.getElementById('confirm');

//get classes by grade
gradeElement.addEventListener('change', function () {
    const grade = gradeElement.value;

    // Xoá label cũ
    document.getElementById('label-class').innerText = "Lớp: "
    document.getElementById('label-subject').innerText = "Môn: "

    // Xóa các option cũ
    classElement.innerHTML = '<option value="">Chọn lớp</option>';
    subjectElement.innerHTML = '<option value="">Chọn môn</option>';

    // Xoá ds học sinh cũ
    document.querySelector('#table-student tbody').innerHTML = '';

    if (grade) {
        fetch(`/get_classes/${grade}`)
            .then(response => response.json())
            .then(classes => {
                classes.forEach(cls => {
                    const option = document.createElement('option');
                    option.value = cls.id;
                    option.textContent = cls.name;
                    classElement.appendChild(option);
                });
            })
            .catch(error => console.error('Error', error));

        fetch(`/get_subjects/${grade}`)
            .then(response => response.json())
            .then(subjects => {
                subjects.forEach(subject => {
                    const option = document.createElement('option');
                    option.value = subject.id;
                    option.textContent = subject.name;
                    subjectElement.appendChild(option);
                });
            })
            .catch(error => console.error('Error', error));
    }
});


classElement.addEventListener('change', () => {
    document.getElementById('label-class').innerText = "Lớp: " + classElement.options[classElement.selectedIndex].text;

    const classId = classElement.value;
    if(classId) {
         fetch('/get_students', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ classId })
        })
            .then(response => response.json())
            .then(data => {
                const tbody = document.querySelector('#table-student tbody');
                tbody.innerHTML = '';
                data.students.forEach((student, index) => {
                    tbody.innerHTML += `
                        <tr>
                            <td>${index+1}</td>
                            <td>${student.full_name}</td>
                            <td>${student.birth}</td>
                            <td><input type="number" step="0.1" min="0" max="10"></td>
                            <td><input type="number" step="0.1" min="0" max="10"></td>
                            <td><input type="number" step="0.1" min="0" max="10"></td>
                        </tr>
                    `;
                });
            });
    }
})

subjectElement.addEventListener('change', () => {
    document.getElementById('label-subject').innerText = "Môn: " + subjectElement.options[subjectElement.selectedIndex].text;
})

semesterElement.addEventListener('change', () => {
    document.getElementById('label-semester').innerText = "Học kỳ: Học kỳ " + semesterElement.value;
})

const d = new Date();
let year = d.getFullYear();
document.getElementById('label-year').innerText = "Năm học: " + year + " " + (year+1);