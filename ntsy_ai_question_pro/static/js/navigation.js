// static/js/navigation.js
document.addEventListener('DOMContentLoaded', function() {
    // 获取导航链接
    const navLinks = document.querySelectorAll('.nav-links .nav-item');
    const pages = {
        'knowledge-base': document.getElementById('knowledge-base-page'),
        'qa-system': document.getElementById('qa-system-page')
    };

    // 根据 URL 设置初始活动状态
    function setInitialActiveState() {
        const currentPath = window.location.pathname;
        navLinks.forEach(link => {
            if (currentPath.includes('knowledge') && link.getAttribute('href').includes('knowledge')) {
                link.classList.add('active');
                if (pages['qa-system']) pages['qa-system'].style.display = 'none';
                if (pages['knowledge-base']) pages['knowledge-base'].style.display = 'block';
            } else if (currentPath === '/' || currentPath.includes('chat')) {
                if (link.getAttribute('href') === '#') {
                    link.classList.add('active');
                    if (pages['qa-system']) pages['qa-system'].style.display = 'block';
                    if (pages['knowledge-base']) pages['knowledge-base'].style.display = 'none';
                }
            }
        });
    }

    // 切换页面显示
    function switchPage(targetPage) {
        Object.values(pages).forEach(page => {
            if (page) {
                page.style.display = 'none';
            }
        });
        if (pages[targetPage]) {
            pages[targetPage].style.display = 'block';
        }
    }

    // 处理导航点击
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') {
                e.preventDefault();
                navLinks.forEach(l => l.classList.remove('active'));
                this.classList.add('active');
                switchPage('qa-system');
            }
            // 知识库管理链接使用默认行为（URL 跳转）
        });
    });

    // 设置初始状态
    setInitialActiveState();
});