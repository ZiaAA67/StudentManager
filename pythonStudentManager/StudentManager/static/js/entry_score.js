let gExamQuantities = {};
let student_ids = [];
const gradeElement = document.getElementById('grade');
const classElement = document.getElementById('class');
const subjectElement = document.getElementById('subject');
const semesterElement = document.getElementById('semester');


classElement.disabled = true;
subjectElement.disabled = true;
semesterElement.disabled = true;


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
        subjectElement.disabled = false;

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
    if (classId) {
        fetch('/get_students', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({classId})
        })
            .then(response => response.json())
            .then(data => {
                student_ids = [] //clear
                const tbody = document.querySelector('#table-student tbody');
                tbody.innerHTML = '';
                data.students.forEach((student, index) => {
                    student_ids.push(student.id)
                    let html = `
                        <tr class="student-row" data-student-id=${student.id}>
                            <td>${index+1}</td>
                            <td>${student.full_name}</td>
                            <td>${student.birth}</td>`

                        for (const [examType, quantity] of Object.entries(gExamQuantities)) {
                            for (let i = 0; i < quantity; i++) {
                                if (examType === 'EXAM_15_MINS') {
                                    html += `<td><input type="number" step="0.1" min="0" max="10" class="EXAM_15_MINS" data-index=${i}></td>`;
                                } else if (examType === 'EXAM_45_MINS') {
                                    html += `<td><input type="number" step="0.1" min="0" max="10" class="EXAM_45_MINS" data-index=${i}></td>`;
                                }
                            }
                        }

                        html += `<td><input type="number" step="0.1" min="0" max="10" class="EXAM_FINAL" data-index="1"></td>
                                 </tr>`

                    tbody.innerHTML += html;
                });
                return student_ids;
            })
            .then(student_ids => {
                loadScores(student_ids);
            });
    }
})

subjectElement.addEventListener('change', () => {
    document.getElementById('label-subject').innerText = "Môn: " + subjectElement.options[subjectElement.selectedIndex].text;

    if(classElement.value) {
        loadScores(student_ids)
    }

    const subjectId = subjectElement.value;
    if (subjectId) {
        semesterElement.disabled = false;

        fetch(`/get_exam_quantities/${subjectId}`)
            .then(response => response.json())
            .then(examQuantities => {
                gExamQuantities = examQuantities;

                let colspan = 0;
                const label = document.getElementById('label');
                label.innerHTML = '';
                let html = `
                    <th>STT</th>
                    <th>Họ tên</th>
                    <th>Ngày sinh</th>
                `

                for (const [examType, quantity] of Object.entries(examQuantities)) {
                    colspan += quantity;
                    for (let i = 0; i < quantity; i++) {
                        if (examType === 'EXAM_15_MINS') {
                            html += `<th>Điểm 15’</th>`;
                        } else if (examType === 'EXAM_45_MINS') {
                            html += `<th>Điểm 1 tiết</th>`;
                        }
                    }
                }

                html += `
                    <th>Điểm thi</th>    
                    </tr>
                `
                label.innerHTML = html;

                document.getElementById('label-semester').setAttribute('colspan', colspan.toString())
                document.getElementById('label-year').setAttribute('colspan', colspan.toString())

            })
            .catch((e) => console.log(e));
    }
})

semesterElement.addEventListener('change', () => {
    document.getElementById('label-semester').innerText = "Học kỳ: Học kỳ " + semesterElement.value;

    if(classElement.value) {
        loadScores(student_ids)
    }

    if(semesterElement.value) {
        classElement.disabled = false;
    }
})

const d = new Date();
let year = d.getFullYear();
document.getElementById('label-year').innerText = "Năm học: " + year + " - " + (year + 1);


document.getElementById('btn-submit').addEventListener('click', async (e) => {
    const classId = classElement.value;
    const subjectId = subjectElement.value;
    const semester = semesterElement.value;

    const scores = [];
    let flags = false;
    document.querySelectorAll(".student-row").forEach(row => {
        const studentId = row.dataset.studentId;

        // Duyệt qua tất cả các loại điểm
        ["EXAM_15_MINS", "EXAM_45_MINS", "EXAM_FINAL"].forEach(scoreType => {
            const scoreInputs = row.querySelectorAll(`.${scoreType}`);
            scoreInputs.forEach(input => {
                const index = input.dataset.index;
                const value = parseFloat(input.value);

                if (!isNaN(value)) {
                    if(value < 0 || value > 10) {
                        console.log(value, typeof value)
                        flags = true;
                    } else {
                        scores.push({
                            studentId,
                            scoreType,
                            index: parseInt(index),
                            score: value,
                        });
                    }
                }
            });
        });
    });

    if(flags) {
        alert("Điểm không hợp lệ, vui lòng kiểm tra lại!");
        return;
    }

    const data = {
        classId: classId,
        subjectId: subjectId,
        semester: semester,
        scores: scores
    };

    try {
        const response = await fetch('/save_scores', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        // Xử lý phản hồi từ server
        const result = await response.json();
        if (response.ok) {
            alert(result.message || "Lưu điểm thành công!");
        } else {
            alert(result.error || "Đã xảy ra lỗi khi lưu điểm.");
        }
    } catch (error) {
        console.error("Lỗi khi gửi request:", error);
        alert("Đã xảy ra lỗi kết nối.");
    }
})


function loadScores(student_ids) {
    const classId = classElement.value;
    const subjectId = subjectElement.value;
    const semester = semesterElement.value;

    fetch('/get_scores', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(
            {
                student_ids,
                classId,
                subjectId,
                semester
            }
        )
    }).then(res => res.json()).then(scores => {
        for (const studentId in scores) {
            const scoreData = scores[studentId];
            const studentRow = document.querySelector(`.student-row[data-student-id="${studentId}"]`);
            if (studentRow) {
                for (const scoreType in scoreData) {
                    const scoresArray = scoreData[scoreType];

                    studentRow.querySelectorAll(`input[class="${scoreType}"]`).forEach((input, index) => {
                        if (index < scoresArray.length) {
                            input.value = scoresArray[index];
                        } else {
                            input.value = '';
                        }
                    });
                }
            }
        }
    })
}




