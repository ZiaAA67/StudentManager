let darkmode = localStorage.getItem('darkmode');
const themeSwitch = document.getElementById('theme-switch');

const enableDarkmode = () => {
    document.body.classList.add('darkmode');  // Sửa lại phần này để thêm class darkmode
    localStorage.setItem('darkmode', 'active');  // Cập nhật trạng thái darkmode
};

const disableDarkmode = () => {
    document.body.classList.remove('darkmode');
    localStorage.setItem('darkmode', null);  // Cập nhật trạng thái darkmode
};

if (darkmode === "active") enableDarkmode();

themeSwitch.addEventListener("click", () => {
    darkmode = localStorage.getItem('darkmode');
    if (darkmode !== "active") {
        enableDarkmode();
    } else {
        disableDarkmode();
    }
});
