// Dark Mode Toggle
(function() {
    // Lấy theme từ localStorage hoặc mặc định là light
    const getTheme = () => {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            return savedTheme;
        }
        // Kiểm tra system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    };

    // Áp dụng theme
    const applyTheme = (theme) => {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        updateToggleButton(theme);
    };

    // Cập nhật nút toggle
    const updateToggleButton = (theme) => {
        const toggleButtons = document.querySelectorAll('.theme-toggle');
        toggleButtons.forEach(btn => {
            if (theme === 'dark') {
                btn.innerHTML = '☀️';
                btn.title = 'Chuyển sang chế độ sáng';
            } else {
                btn.innerHTML = '🌙';
                btn.title = 'Chuyển sang chế độ tối';
            }
        });
        
        // Cập nhật icon và text trong dropdown
        const themeIcon = document.getElementById('theme-icon');
        const themeText = document.getElementById('theme-text');
        if (themeIcon && themeText) {
            if (theme === 'dark') {
                themeIcon.textContent = '☀️';
                themeText.textContent = 'Chế độ sáng';
            } else {
                themeIcon.textContent = '🌙';
                themeText.textContent = 'Chế độ tối';
            }
        }
    };

    // Toggle theme
    const toggleTheme = () => {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        applyTheme(newTheme);
    };
    
    // Export toggleTheme để có thể gọi từ HTML
    window.toggleTheme = toggleTheme;

    // Khởi tạo theme khi trang load
    document.addEventListener('DOMContentLoaded', () => {
        const theme = getTheme();
        applyTheme(theme);
        
        // Thêm event listener cho các nút toggle
        document.querySelectorAll('.theme-toggle').forEach(btn => {
            btn.addEventListener('click', toggleTheme);
        });
    });

    // Lắng nghe thay đổi system preference (chỉ khi chưa có preference được lưu)
    if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('theme')) {
                applyTheme(e.matches ? 'dark' : 'light');
            }
        });
    }
})();

