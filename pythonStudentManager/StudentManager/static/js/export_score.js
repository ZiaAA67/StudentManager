const gradeElement = document.getElementById('grade');
const classElement = document.getElementById('class');
const semesterElement = document.getElementById('semester');

let totalSubjects = 0;
let student_ids = []
let subject_ids = []

classElement.disabled = true;
semesterElement.disabled = true;

const d = new Date();
let year = d.getFullYear();
document.getElementById('label-year').innerText = "Năm học: " + year + " - " + (year + 1);

//get classes by grade
gradeElement.addEventListener('change', function () {
    const grade = gradeElement.value;

    // Xoá label, option cũ
    document.getElementById('label-class').innerText = "Lớp: "
    classElement.innerHTML = '<option value="">Chọn lớp</option>';

    // Xoá ds học sinh cũ
    document.querySelector('#table-student tbody').innerHTML = '';

    if (grade) {
        semesterElement.disabled = false;

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
                const heading = document.getElementById('label-header');
                heading.innerHTML = "";

                let html = `
                    <th>STT</th>
                    <th>Họ tên</th>
                    <th>Ngày sinh</th>
                `

                subject_ids = [];
                subjects.forEach(s => {
                    subject_ids.push(s.id);
                    html += `<th>${capitalize(s.name)}</th>`
                })

                html += `<th id="avg-label">Điểm trung bình</th>`

                heading.innerHTML = html;

                totalSubjects = subjects.length + 1;
                document.getElementById('label-year').setAttribute('colspan', totalSubjects.toString())
                document.getElementById('label-semester').setAttribute('colspan', totalSubjects.toString())

            })
            .catch(error => console.error('Error', error));
    }
})


semesterElement.addEventListener('change', () => {
    const avgLabel = document.getElementById('avg-label');
    const semesterLabel = document.getElementById('label-semester');

    if(parseInt(semesterElement.value) ===  3) {
        semesterLabel.innerText = "Tổng kết năm học";
        avgLabel.innerText = "Điểm TB năm học"
    } else {
        semesterLabel.innerText = "Học kỳ: Học kỳ " + semesterElement.value;
        avgLabel.innerText = "Điểm TB HK" + semesterElement.value;
    }

    if(semesterElement.value) {
        classElement.disabled = false;
    }

    if(classElement.value) {
        loadAvgScores(student_ids, subject_ids)
    }
})


classElement.addEventListener('change', () => {
    document.getElementById('label-class').innerText = "Lớp: " + classElement.options[classElement.selectedIndex].text;

    const classId = classElement.value;
    if (classId) {
        fetch('/get_students', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({classId})
        })
            .then(response => response.json())
            .then(data => {
                const tbody = document.querySelector('#table-student tbody');
                tbody.innerHTML = '';

                student_ids = [];
                data.students.forEach((student, index) => {
                    student_ids.push(student.id);
                    let html = `
                        <tr class="student-row" data-student-id=${student.id}>
                            <td>${index+1}</td>
                            <td>${student.full_name}</td>
                            <td>${student.birth}</td>`

                    for(const subject_id of subject_ids) {
                        html += `<td><input type="number" step="0.1" min="0" max="10" data-subject-id=${subject_id} readonly></td>`
                    }

                    html += `
                        <td><input type="number" step="0.1" min="0" max="10" data-subject-id=0 readonly></td>
                        </tr>`
                    tbody.innerHTML += html;
                });
            })
            .then(() => {
                loadAvgScores(student_ids, subject_ids);
            })
    }
})

function loadAvgScores(student_ids, subject_ids) {
    const classId = classElement.value;
    const semester = semesterElement.value;

    const inputs = document.querySelectorAll("input[data-subject-id]")
    inputs.forEach(i => i.value = '')

    fetch('/get_avg_scores', {
        method: 'POST',
        body: JSON.stringify({
            'classId': classId,
            'semester': semester,
            'students': student_ids,
            'subjects': subject_ids
        }),
        headers: {'Content-Type': 'application/json'}
    })
        .then(responsive => responsive.json())
        .then(averages => {
            for (const studentId in averages) {
                const studentData = averages[studentId];

                const subjects = studentData.subjects;

                for (const subjectId in subjects) {
                    const averageScore = subjects[subjectId].average;

                    const input = document.querySelector(`.student-row[data-student-id="${studentId}"] input[data-subject-id="${subjectId}"]`);

                    if (input) {
                        input.value = averageScore;
                    }
                }

                document.querySelector(`.student-row[data-student-id="${studentId}"] input[data-subject-id="0"]`).value = studentData.overall_average;
            }
        })
}

document.querySelector('.btn-export').addEventListener('click', () => {
    window.print();
})

function capitalize(s) {
    return String(s[0]).toUpperCase() + String(s).slice(1);
}