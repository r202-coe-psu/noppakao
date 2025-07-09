const toggleBtn = document.getElementById('toggleBtn');
const sidebar = document.getElementById('sidebar');
const sidebarMenu = document.getElementById('sidebar-menu');
const texts = document.querySelectorAll('.sidebar-text');
const toggleIcon = document.getElementById('toggleIcon');
const containerContent = document.getElementById('container-content');

let collapsed = false;
toggleBtn.addEventListener('click', () => {
    collapsed = !collapsed;
    if (collapsed) {
        sidebar.classList.replace('w-72', 'w-[80px]');
        toggleBtn.classList.replace('left-68', 'left-16');
        texts.forEach(t => t.classList.add('opacity-0'));
    } else {
        sidebar.classList.replace('w-[80px]', 'w-72');
        toggleBtn.classList.replace('left-16', 'left-68');
        texts.forEach(t => t.classList.remove('opacity-0'));
    }
    toggleIcon.classList.toggle('rotate-180');
});