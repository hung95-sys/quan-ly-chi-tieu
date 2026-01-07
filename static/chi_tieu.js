// Đợi DOM load xong
document.addEventListener('DOMContentLoaded', function () {

    // Load mục đích quỹ
    let quyPurposes = [];
    let quyPurposesThu = [];
    let quyPurposesChi = [];

    async function loadQuyPurposes() {
        try {
            const res = await fetch('/api/quy_purposes');
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Không tải được mục đích quỹ');
            quyPurposes = data.purposes || [];
            // Cập nhật dropdown cho tab Chi tiêu/Thu nhập
            const purposeSelect = document.getElementById('muc-dich-quy');
            if (purposeSelect) {
                purposeSelect.innerHTML = '<option value="">Chọn mục đích...</option>' +
                    quyPurposes.map(p => `<option value="${p.name}">${p.icon || ''} ${p.name}</option>`).join('');
            }
        } catch (err) {
            console.error('Lỗi load mục đích quỹ:', err);
        }
    }

    async function loadQuyPurposesThu() {
        try {
            console.log('Đang load mục đích quỹ Thu...');
            const res = await fetch('/api/quy_purposes_thu');
            if (!res.ok) {
                const errorData = await res.json().catch(() => ({}));
                throw new Error(errorData.error || 'Không tải được mục đích quỹ Thu');
            }
            const data = await res.json();
            quyPurposesThu = data.purposes || [];
            console.log('Mục đích quỹ Thu nhận được:', quyPurposesThu);

            const purposeGrid = document.getElementById('muc-dich-quy-thu-grid');
            if (purposeGrid) {
                purposeGrid.innerHTML = '';
                console.log('Đang render', quyPurposesThu.length, 'mục đích quỹ Thu');

                quyPurposesThu.forEach((purpose, index) => {
                    const btn = document.createElement('button');
                    btn.type = 'button';
                    btn.className = 'chi-cat' + (index === 0 ? ' active' : '');
                    btn.dataset.purpose = purpose.name;

                    // Hiển thị icon và tên
                    btn.innerHTML = (purpose.icon || '') + ' ' + purpose.name;

                    btn.addEventListener('click', function () {
                        document.querySelectorAll('#muc-dich-quy-thu-grid .chi-cat').forEach(b => b.classList.remove('active'));
                        this.classList.add('active');
                    });

                    purposeGrid.appendChild(btn);
                });
                console.log('Đã render xong mục đích quỹ Thu');
            } else {
                console.error('Không tìm thấy muc-dich-quy-thu-grid');
            }
        } catch (err) {
            console.error('Lỗi load mục đích quỹ Thu:', err);
            alert('Lỗi khi tải mục đích quỹ: ' + err.message);
        }
    }

    async function loadQuyPurposesChi() {
        try {
            console.log('Đang load mục đích quỹ Chi...');
            const res = await fetch('/api/quy_purposes_chi');
            if (!res.ok) {
                const errorData = await res.json().catch(() => ({}));
                throw new Error(errorData.error || 'Không tải được mục đích quỹ Chi');
            }
            const data = await res.json();
            quyPurposesChi = data.purposes || [];
            console.log('Mục đích quỹ Chi nhận được:', quyPurposesChi);

            const purposeGrid = document.getElementById('muc-dich-quy-chi-grid');
            if (purposeGrid) {
                purposeGrid.innerHTML = '';
                console.log('Đang render', quyPurposesChi.length, 'mục đích quỹ Chi');

                quyPurposesChi.forEach((purpose, index) => {
                    const btn = document.createElement('button');
                    btn.type = 'button';
                    btn.className = 'chi-cat' + (index === 0 ? ' active' : '');
                    btn.dataset.purpose = purpose.name;

                    // Hiển thị icon và tên
                    btn.innerHTML = (purpose.icon || '') + ' ' + purpose.name;

                    btn.addEventListener('click', function () {
                        document.querySelectorAll('#muc-dich-quy-chi-grid .chi-cat').forEach(b => b.classList.remove('active'));
                        this.classList.add('active');
                    });

                    purposeGrid.appendChild(btn);
                });
                console.log('Đã render xong mục đích quỹ Chi');
            } else {
                console.error('Không tìm thấy muc-dich-quy-chi-grid');
            }
        } catch (err) {
            console.error('Lỗi load mục đích quỹ Chi:', err);
            alert('Lỗi khi tải mục đích quỹ: ' + err.message);
        }
    }

    // Load danh mục từ API
    async function loadCategories(type = 'Chi') {
        try {
            console.log(`Đang load danh mục ${type}...`);
            const response = await fetch(`/api/categories?type=${type}`);
            const data = await response.json();
            console.log(`Danh mục ${type} nhận được:`, data);

            const categoriesGrid = document.getElementById('categories-grid');
            if (categoriesGrid) {
                if (data.categories && data.categories.length > 0) {
                    categoriesGrid.innerHTML = '';
                    console.log('Đang render', data.categories.length, 'danh mục');

                    data.categories.forEach((category, index) => {
                        const btn = document.createElement('button');
                        btn.type = 'button';
                        btn.className = 'chi-cat' + (index === 0 ? ' active' : '');

                        // Giữ nguyên toàn bộ giá trị từ cột B (bao gồm tất cả icon và text)
                        // Category có thể chứa nhiều icon emoji và text, ví dụ: "💰⚡ Điện"
                        btn.dataset.category = category;

                        // Hiển thị toàn bộ giá trị từ cột B (bao gồm icon và text)
                        // Sử dụng innerHTML để giữ nguyên emoji/icon
                        btn.innerHTML = category;

                        btn.addEventListener('click', function () {
                            document.querySelectorAll('.chi-cat').forEach(b => b.classList.remove('active'));
                            this.classList.add('active');

                            // Hiển thị dropdown mục đích quỹ nếu chọn "Quỹ"
                            const purposeField = document.getElementById('muc-dich-quy-field');
                            const selectedCategory = this.dataset.category || '';
                            if (purposeField) {
                                if (selectedCategory && selectedCategory.toLowerCase().includes('quỹ')) {
                                    purposeField.style.display = 'block';
                                } else {
                                    purposeField.style.display = 'none';
                                    const purposeSelect = document.getElementById('muc-dich-quy');
                                    if (purposeSelect) purposeSelect.value = '';
                                }
                            }
                        });

                        categoriesGrid.appendChild(btn);
                    });
                    console.log('Đã render xong danh mục');
                } else {
                    // Nếu không có danh mục, xóa grid và hiện thông báo
                    categoriesGrid.innerHTML = '<div class="chi-cat placeholder">Chưa có danh mục</div>';
                    console.log('Không có danh mục từ API');
                }
            } else {
                console.error('Không tìm thấy categories-grid');
            }
        } catch (error) {
            console.error('Lỗi khi load danh mục:', error);
        }
    }

    // Load danh mục khi trang load (mặc định là Chi)
    loadCategories('Chi');
    // Load mục đích quỹ
    loadQuyPurposes();
    loadQuyPurposesThu();
    loadQuyPurposesChi();

    // Xử lý chọn danh mục (cho các danh mục mặc định nếu API không có)
    document.querySelectorAll('.chi-cat').forEach(btn => {
        btn.addEventListener('click', function () {
            document.querySelectorAll('.chi-cat').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Xử lý ngày
    let currentDate = new Date();
    const ngayInput = document.getElementById('ngay');

    function formatDate(date) {
        const days = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'];
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        const dayName = days[date.getDay()];
        return `${day}/${month}/${year} (${dayName})`;
    }

    function updateDate() {
        ngayInput.value = formatDate(currentDate);
    }

    document.getElementById('prev-day').addEventListener('click', () => {
        currentDate.setDate(currentDate.getDate() - 1);
        updateDate();
    });

    document.getElementById('next-day').addEventListener('click', () => {
        currentDate.setDate(currentDate.getDate() + 1);
        updateDate();
    });

    updateDate();

    // Format số tiền với dấu chấm ngăn cách
    const soTienInput = document.getElementById('so-tien');

    function formatMoneyInput(inputEl) {
        const raw = inputEl.value.replace(/\D/g, '');
        if (!raw) {
            inputEl.value = '';
            return '';
        }
        const formatted = raw.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
        inputEl.value = formatted;
        return formatted;
    }

    function parseNumber(value) {
        if (!value || value === '') return 0;
        // Loại bỏ dấu chấm để lấy số thực
        const numStr = value.replace(/\./g, '').trim();
        if (!numStr) return 0;
        // Sử dụng Number thay vì parseInt để hỗ trợ số lớn hơn
        const num = Number(numStr);
        // Kiểm tra NaN
        return isNaN(num) ? 0 : num;
    }

    if (soTienInput) {
        // Đảm bảo không có giới hạn maxlength
        soTienInput.removeAttribute('maxlength');
        soTienInput.removeAttribute('max');

        // Format ngay trong khi nhập với dấu chấm tách hàng nghìn (theo sample)
        soTienInput.addEventListener('input', function () {
            formatMoneyInput(this);
        });

        // Thêm hiệu ứng focus
        soTienInput.addEventListener('focus', function () {
            this.parentElement.classList.add('focused');
        });

        soTienInput.addEventListener('blur', function () {
            this.parentElement.classList.remove('focused');
        });
    }

    // Mở calendar khi click vào input ngày
    if (ngayInput) {
        ngayInput.addEventListener('click', (e) => {
            e.preventDefault();
            openCalendar();
        });
    } else {
        console.error('ngayInput not found!');
    }

    // Calendar functionality
    let calendarCurrentDate = new Date(currentDate);
    const calendarModal = document.getElementById('calendar-modal');
    const calendarOverlay = document.getElementById('calendar-overlay');
    const calendarDays = document.getElementById('calendar-days');
    const calendarMonthYear = document.getElementById('calendar-month-year');
    const calendarPrevMonth = document.getElementById('calendar-prev-month');
    const calendarNextMonth = document.getElementById('calendar-next-month');

    function openCalendar() {
        if (!calendarModal) {
            console.error('Calendar modal not found!');
            return;
        }
        calendarCurrentDate = new Date(currentDate);
        renderCalendar();
        calendarModal.style.display = 'flex';
        // Đảm bảo calendar ở giữa màn hình
        calendarModal.style.alignItems = 'center';
        calendarModal.style.justifyContent = 'center';
    }

    function closeCalendar() {
        if (calendarModal) {
            calendarModal.style.display = 'none';
        }
    }

    function renderCalendar() {
        const year = calendarCurrentDate.getFullYear();
        const month = calendarCurrentDate.getMonth();

        // Hiển thị tháng/năm
        const monthNames = ['Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5', 'Tháng 6',
            'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12'];
        calendarMonthYear.textContent = `${monthNames[month]} ${year}`;

        // Lấy ngày đầu tiên của tháng và số ngày trong tháng
        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();

        // Clear calendar
        calendarDays.innerHTML = '';

        // Thêm các ô trống cho ngày đầu tuần
        for (let i = 0; i < firstDay; i++) {
            const emptyCell = document.createElement('div');
            emptyCell.className = 'calendar-day empty';
            calendarDays.appendChild(emptyCell);
        }

        // Thêm các ngày trong tháng
        for (let day = 1; day <= daysInMonth; day++) {
            const dayCell = document.createElement('div');
            dayCell.className = 'calendar-day';
            dayCell.textContent = day;

            // Highlight ngày hiện tại (hôm nay)
            const today = new Date();
            if (day === today.getDate() &&
                month === today.getMonth() &&
                year === today.getFullYear()) {
                dayCell.classList.add('today');
            }

            // Highlight ngày được chọn
            if (day === currentDate.getDate() &&
                month === currentDate.getMonth() &&
                year === currentDate.getFullYear()) {
                dayCell.classList.add('selected');
            }

            dayCell.addEventListener('click', () => {
                currentDate = new Date(year, month, day);
                updateDate();
                closeCalendar();
            });

            calendarDays.appendChild(dayCell);
        }
    }

    if (calendarPrevMonth) {
        calendarPrevMonth.addEventListener('click', () => {
            calendarCurrentDate.setMonth(calendarCurrentDate.getMonth() - 1);
            renderCalendar();
        });
    }

    if (calendarNextMonth) {
        calendarNextMonth.addEventListener('click', () => {
            calendarCurrentDate.setMonth(calendarCurrentDate.getMonth() + 1);
            renderCalendar();
        });
    }

    if (calendarOverlay) {
        calendarOverlay.addEventListener('click', closeCalendar);
    }

    // Khai báo biến currentType trước khi sử dụng trong event listener
    let currentType = 'Chi'; // 'Chi', 'Thu', 'ThuQuy', hoặc 'ChiQuy'

    // Xử lý form submit
    const expenseForm = document.getElementById('expense-form');
    const submitBtnClick = document.getElementById('submit-btn');

    if (!expenseForm) {
        console.error('Không tìm thấy form expense-form');
    } else {
        console.log('Form expense-form đã tìm thấy');
    }

    if (!submitBtnClick) {
        console.error('Không tìm thấy nút submit-btn');
    } else {
        console.log('Nút submit-btn đã tìm thấy');
        // Đảm bảo button không bị disabled
        submitBtnClick.disabled = false;
    }

    // Thêm event listener cho form submit
    expenseForm?.addEventListener('submit', async (e) => {
        console.log('Submit event được trigger');
        e.preventDefault();
        e.stopPropagation();
        console.log('Form submit được gọi, currentType:', currentType);

        // Format ngày: DD/MM/YYYY
        const day = String(currentDate.getDate()).padStart(2, '0');
        const month = String(currentDate.getMonth() + 1).padStart(2, '0');
        const year = currentDate.getFullYear();
        const ngay = `${day}/${month}/${year}`;
        const ghiChu = document.getElementById('ghi-chu').value.trim();
        const soTienVal = (document.getElementById('so-tien').value || '').trim().replace(/\./g, '');

        console.log('Dữ liệu form:', { ngay, ghiChu, soTienVal, currentType });

        let selectedCategory = '';
        let mucDichQuy = '';
        let loaiToSubmit = currentType;

        // Xử lý theo loại tab
        if (currentType === 'ThuQuy') {
            // Tab Thu quỹ: lấy tiền từ số dư (thu nhập) để bỏ vào quỹ → tăng quỹ
            console.log('Xử lý tab Thu quỹ');
            const purposeBtn = document.querySelector('#muc-dich-quy-thu-grid .chi-cat.active');
            const purposeVal = purposeBtn?.dataset.purpose || '';
            console.log('Danh mục Thu quỹ:', purposeVal);
            if (!purposeVal) {
                alert('Vui lòng chọn danh mục');
                return;
            }
            if (!soTienVal) {
                alert('Vui lòng nhập số tiền');
                return;
            }
            mucDichQuy = purposeVal;
            selectedCategory = 'Thu quỹ';
            loaiToSubmit = 'Thu'; // Luôn là Thu (tăng quỹ)
        } else if (currentType === 'ChiQuy') {
            // Tab Chi quỹ: lấy tiền từ quỹ để chi → giảm quỹ
            console.log('Xử lý tab Chi quỹ');
            const purposeBtn = document.querySelector('#muc-dich-quy-chi-grid .chi-cat.active');
            const purposeVal = purposeBtn?.dataset.purpose || '';
            console.log('Danh mục Chi quỹ:', purposeVal);
            if (!purposeVal) {
                alert('Vui lòng chọn danh mục');
                return;
            }
            if (!soTienVal) {
                alert('Vui lòng nhập số tiền');
                return;
            }
            mucDichQuy = purposeVal;
            selectedCategory = 'Chi quỹ';
            loaiToSubmit = 'Chi'; // Luôn là Chi (giảm quỹ)
        } else {
            // Tab Chi tiêu hoặc Thu nhập: cần danh mục (LOGIC CŨ - KHÔNG SỬA)
            console.log('Xử lý tab Chi tiêu hoặc Thu nhập');
            selectedCategory = document.querySelector('.chi-cat.active')?.dataset.category || '';
            console.log('Danh mục đã chọn:', selectedCategory);
            if (!selectedCategory || !soTienVal) {
                alert('Vui lòng chọn danh mục và nhập số tiền');
                return;
            }

            // Kiểm tra mục đích quỹ nếu chọn category "Quỹ"
            if (selectedCategory && selectedCategory.toLowerCase().includes('quỹ')) {
                const purposeVal = (document.getElementById('muc-dich-quy')?.value || '').trim();
                if (!purposeVal) {
                    alert('Vui lòng chọn danh mục');
                    return;
                }
                mucDichQuy = purposeVal;
            }
        }

        console.log('Sau validation:', { selectedCategory, mucDichQuy, loaiToSubmit });

        const soTien = parseNumber(soTienVal);
        console.log('Số tiền đã parse:', soTien);
        if (soTien <= 0) {
            alert('Số tiền phải lớn hơn 0');
            return;
        }

        // Sử dụng biến submitBtn đã khai báo ở ngoài
        // Kiểm tra lại để đảm bảo tồn tại
        const submitBtnLocal = document.getElementById('submit-btn');
        if (!submitBtnLocal) {
            console.error('Không tìm thấy nút submit-btn trong submit handler');
            alert('Lỗi: Không tìm thấy nút submit');
            return;
        }

        // Kiểm tra xem button có bị disabled không
        if (submitBtnLocal.disabled) {
            console.warn('Button đã bị disabled, bỏ qua submit');
            return;
        }

        console.log('Bắt đầu submit, disable button');
        submitBtnLocal.disabled = true;
        submitBtnLocal.textContent = 'Đang lưu...';

        console.log('Chuẩn bị gửi request:', {
            ngay, loai: loaiToSubmit, danh_muc: selectedCategory,
            so_tien: soTien, ghi_chu: ghiChu, quy: mucDichQuy
        });

        try {
            const response = await fetch('/api/expenses', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    ngay: ngay,
                    loai: loaiToSubmit, // 'Chi' hoặc 'Thu'
                    danh_muc: selectedCategory,
                    so_tien: soTien,
                    ghi_chu: ghiChu,
                    quy: mucDichQuy // Mục đích quỹ (có khi category='Quỹ')
                })
            });

            const data = await response.json();

            if (data.success) {
                let message = '';
                if (currentType === 'ThuQuy') {
                    message = 'Thu vào quỹ thành công!';
                } else if (currentType === 'ChiQuy') {
                    message = 'Chi từ quỹ thành công!';
                } else {
                    message = loaiToSubmit === 'Chi' ? 'Thêm chi tiêu thành công!' : 'Thêm thu nhập thành công!';
                }
                alert(message);
                // Reset form
                document.getElementById('ghi-chu').value = '';
                document.getElementById('so-tien').value = '';
                // Ẩn mục đích quỹ
                const purposeField = document.getElementById('muc-dich-quy-field');
                if (purposeField) {
                    purposeField.style.display = 'none';
                    const purposeSelect = document.getElementById('muc-dich-quy');
                    if (purposeSelect) purposeSelect.value = '';
                }
                // Reset mục đích quỹ Thu quỹ
                const purposeThuField = document.getElementById('muc-dich-quy-thu-field');
                if (purposeThuField) {
                    // Reset selection
                    document.querySelectorAll('#muc-dich-quy-thu-grid .chi-cat').forEach(btn => {
                        btn.classList.remove('active');
                    });
                    // Chọn button đầu tiên
                    const firstBtn = document.querySelector('#muc-dich-quy-thu-grid .chi-cat');
                    if (firstBtn) firstBtn.classList.add('active');
                    // Nếu đang ở tab Thu quỹ, giữ hiển thị field
                    if (currentType === 'ThuQuy') {
                        purposeThuField.style.display = 'block';
                    } else {
                        purposeThuField.style.display = 'none';
                    }
                }
                // Reset mục đích quỹ Chi quỹ
                const purposeChiField = document.getElementById('muc-dich-quy-chi-field');
                if (purposeChiField) {
                    // Reset selection
                    document.querySelectorAll('#muc-dich-quy-chi-grid .chi-cat').forEach(btn => {
                        btn.classList.remove('active');
                    });
                    // Chọn button đầu tiên
                    const firstBtn = document.querySelector('#muc-dich-quy-chi-grid .chi-cat');
                    if (firstBtn) firstBtn.classList.add('active');
                    // Nếu đang ở tab Chi quỹ, giữ hiển thị field
                    if (currentType === 'ChiQuy') {
                        purposeChiField.style.display = 'block';
                    } else {
                        purposeChiField.style.display = 'none';
                    }
                }
                // Chọn danh mục đầu tiên
                const firstCategory = document.querySelector('.chi-cat');
                if (firstCategory) {
                    document.querySelectorAll('.chi-cat').forEach(b => b.classList.remove('active'));
                    firstCategory.classList.add('active');
                }
                // Luôn reset lichData để khi chuyển sang lịch sẽ reload dữ liệu mới
                lichData = null;
                // Nếu đang ở view lịch, reload dữ liệu ngay
                if (lichSection && lichSection.style.display !== 'none') {
                    loadLichData(true).then(data => {
                        if (data) {
                            renderLichCalendar();
                            renderLichTransactions();
                            updateLichSummary();
                        }
                    });
                }
            } else {
                let errorMsg = 'Không thể lưu';
                if (currentType === 'Chi') {
                    errorMsg = 'Không thể lưu chi tiêu';
                } else if (currentType === 'Thu') {
                    errorMsg = 'Không thể lưu thu nhập';
                } else if (currentType === 'ThuQuy') {
                    errorMsg = 'Không thể thu vào quỹ';
                } else if (currentType === 'ChiQuy') {
                    errorMsg = 'Không thể chi từ quỹ';
                }
                alert('Lỗi: ' + (data.error || errorMsg));
            }
        } catch (error) {
            console.error('Lỗi khi submit form:', error);
            alert('Lỗi: ' + error.message);
        } finally {
            // Luôn enable lại button và cập nhật text
            const submitBtnFinal = document.getElementById('submit-btn');
            if (submitBtnFinal) {
                submitBtnFinal.disabled = false;
                // Cập nhật text button theo tab hiện tại
                if (currentType === 'Chi') {
                    submitBtnFinal.textContent = 'Nhập khoản Tiền chi';
                } else if (currentType === 'Thu') {
                    submitBtnFinal.textContent = 'Nhập khoản Tiền thu';
                } else if (currentType === 'ThuQuy') {
                    submitBtnFinal.textContent = 'Thu vào quỹ';
                } else if (currentType === 'ChiQuy') {
                    submitBtnFinal.textContent = 'Chi từ quỹ';
                }
            } else {
                console.error('Không tìm thấy submitBtn trong finally block');
            }
        }
    });

    // Xử lý bottom navigation - switch giữa form và lịch (khai báo trước để dùng trong switchTab)
    const formSection = document.getElementById('form-section');
    const lichSection = document.getElementById('lich-section');
    const navNhapVao = document.getElementById('nav-nhap-vao');
    const navLich = document.getElementById('nav-lich');

    // Xử lý tabs
    const tabChiTieu = document.getElementById('tab-chi-tieu');
    const tabThuNhap = document.getElementById('tab-thu-nhap');
    const tabThuQuy = document.getElementById('tab-thu-quy');
    const tabChiQuy = document.getElementById('tab-chi-quy');
    const tienLabel = document.getElementById('tien-label');
    const submitBtn = document.getElementById('submit-btn');
    const danhMucField = document.getElementById('danh-muc-field');
    const categoriesGrid = document.getElementById('categories-grid');
    const mucDichQuyField = document.getElementById('muc-dich-quy-field');
    const mucDichQuyThuField = document.getElementById('muc-dich-quy-thu-field');
    const mucDichQuyChiField = document.getElementById('muc-dich-quy-chi-field');
    // currentType đã được khai báo ở trên (dòng 562)

    function switchTab(type) {
        console.log('switchTab được gọi với type:', type);
        currentType = type;

        // Chuyển về form section khi nhấn tab
        if (formSection && lichSection && navNhapVao && navLich) {
            formSection.style.display = 'block';
            lichSection.style.display = 'none';
            navNhapVao.classList.add('active');
            navLich.classList.remove('active');
        }

        // Reset tất cả tabs
        tabChiTieu?.classList.remove('active');
        tabThuNhap?.classList.remove('active');
        tabThuQuy?.classList.remove('active');
        tabChiQuy?.classList.remove('active');

        // Ẩn tất cả các field đặc biệt
        if (mucDichQuyField) mucDichQuyField.style.display = 'none';
        if (mucDichQuyThuField) mucDichQuyThuField.style.display = 'none';
        if (mucDichQuyChiField) mucDichQuyChiField.style.display = 'none';
        // Hiển thị field danh mục mặc định
        if (danhMucField) danhMucField.style.display = 'block';
        if (categoriesGrid) categoriesGrid.style.display = 'grid';

        // Cập nhật theo từng loại tab
        if (type === 'Chi') {
            console.log('Chuyển sang tab Chi tiêu');
            tabChiTieu?.classList.add('active');
            tienLabel.textContent = 'Tiền chi';
            submitBtn.textContent = 'Nhập khoản Tiền chi';
            loadCategories('Chi');
        } else if (type === 'Thu') {
            console.log('Chuyển sang tab Thu nhập');
            tabThuNhap?.classList.add('active');
            tienLabel.textContent = 'Tiền thu';
            submitBtn.textContent = 'Nhập khoản Tiền thu';
            loadCategories('Thu');
        } else if (type === 'ThuQuy') {
            console.log('Chuyển sang tab Thu quỹ');
            if (!tabThuQuy) {
                console.error('tabThuQuy không tồn tại!');
                return;
            }
            tabThuQuy.classList.add('active');
            tienLabel.textContent = 'Số tiền thu vào quỹ';
            submitBtn.textContent = 'Thu vào quỹ';
            // Ẩn danh mục, hiển thị mục đích quỹ
            if (danhMucField) {
                danhMucField.style.display = 'none';
                console.log('Đã ẩn danhMucField');
            }
            if (mucDichQuyThuField) {
                mucDichQuyThuField.style.display = 'block';
                console.log('Đã hiển thị mucDichQuyThuField');
                // Load danh sách mục đích quỹ Thu
                loadQuyPurposesThu();
            } else {
                console.error('mucDichQuyThuField không tồn tại!');
            }
        } else if (type === 'ChiQuy') {
            console.log('Chuyển sang tab Chi quỹ');
            if (!tabChiQuy) {
                console.error('tabChiQuy không tồn tại!');
                return;
            }
            tabChiQuy.classList.add('active');
            tienLabel.textContent = 'Số tiền chi từ quỹ';
            submitBtn.textContent = 'Chi từ quỹ';
            // Ẩn danh mục, hiển thị mục đích quỹ
            if (danhMucField) {
                danhMucField.style.display = 'none';
                console.log('Đã ẩn danhMucField');
            }
            if (mucDichQuyChiField) {
                mucDichQuyChiField.style.display = 'block';
                console.log('Đã hiển thị mucDichQuyChiField');
                // Load danh sách mục đích quỹ Chi
                loadQuyPurposesChi();
            } else {
                console.error('mucDichQuyChiField không tồn tại!');
            }
        }
    }

    if (tabChiTieu) {
        tabChiTieu.addEventListener('click', () => {
            switchTab('Chi');
        });
    }

    if (tabThuNhap) {
        tabThuNhap.addEventListener('click', () => {
            switchTab('Thu');
        });
    }

    if (tabThuQuy) {
        tabThuQuy.addEventListener('click', () => {
            console.log('Tab Thu quỹ được click');
            switchTab('ThuQuy');
        });
    } else {
        console.error('Không tìm thấy tab-thu-quy');
    }

    if (tabChiQuy) {
        tabChiQuy.addEventListener('click', () => {
            console.log('Tab Chi quỹ được click');
            switchTab('ChiQuy');
        });
    } else {
        console.error('Không tìm thấy tab-chi-quy');
    }

    // Thêm event listener trực tiếp vào button để đảm bảo submit hoạt động
    if (submitBtnClick) {
        submitBtnClick.addEventListener('click', async (e) => {
            console.log('Button submit được click trực tiếp');
            // Trigger form submit
            if (expenseForm) {
                expenseForm.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
            }
        });
    }

    let lichData = null;
    let lichCurrentDate = new Date();
    let lichPopupDate = new Date(); // Date cho popup calendar

    // Load dữ liệu lịch
    async function loadLichData(forceReload = false) {
        if (lichData && !forceReload) return lichData;

        const year = lichCurrentDate.getFullYear();
        const month = lichCurrentDate.getMonth() + 1; // JavaScript month is 0-based

        try {
            const response = await fetch(`/api/calendar?month=${month}&year=${year}`);
            const data = await response.json();
            lichData = data;
            return data;
        } catch (error) {
            console.error('Lỗi khi load dữ liệu lịch:', error);
            return null;
        }
    }

    // Render calendar
    function renderLichCalendar() {
        const calendarDays = document.getElementById('lich-calendar-days');
        const monthYear = document.getElementById('lich-month-year');
        if (!calendarDays || !monthYear) return;

        const year = lichCurrentDate.getFullYear();
        const month = lichCurrentDate.getMonth();

        const monthNames = ['Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5', 'Tháng 6',
            'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12'];
        monthYear.textContent = `${monthNames[month]} ${year}`;

        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const adjustedFirstDay = (firstDay === 0) ? 6 : firstDay - 1;

        calendarDays.innerHTML = '';

        // Empty cells
        for (let i = 0; i < adjustedFirstDay; i++) {
            const emptyCell = document.createElement('div');
            emptyCell.className = 'chi-lich-day empty';
            calendarDays.appendChild(emptyCell);
        }

        // Days
        const today = new Date();
        for (let day = 1; day <= daysInMonth; day++) {
            const dayCell = document.createElement('div');
            dayCell.className = 'chi-lich-day';

            const dateObj = new Date(year, month, day);
            const dateKey = formatDateKey(dateObj);
            const totals = lichData?.daily_totals?.[dateKey] || { thu: 0, chi: 0 };

            const dayNum = document.createElement('div');
            dayNum.className = 'chi-lich-day-number';
            dayNum.textContent = day;
            dayCell.appendChild(dayNum);

            // Hiển thị cả thu và chi nếu có
            if (totals.thu > 0) {
                const thuDiv = document.createElement('div');
                thuDiv.className = 'chi-lich-day-amount thu';
                thuDiv.textContent = totals.thu.toLocaleString('vi-VN');
                dayCell.appendChild(thuDiv);
            }

            if (totals.chi > 0) {
                const chiDiv = document.createElement('div');
                chiDiv.className = 'chi-lich-day-amount chi';
                chiDiv.textContent = totals.chi.toLocaleString('vi-VN');
                dayCell.appendChild(chiDiv);
            }

            // Highlight nếu có giao dịch
            if (totals.thu > 0 || totals.chi > 0) {
                dayCell.style.background = '#fff7ed';
            }

            if (day === today.getDate() && month === today.getMonth() && year === today.getFullYear()) {
                dayCell.classList.add('today');
            }

            dayCell.addEventListener('click', () => {
                // Remove selected class from all days
                document.querySelectorAll('.chi-lich-day').forEach(d => d.classList.remove('selected'));
                // Add selected class to clicked day
                dayCell.classList.add('selected');
                // Scroll to transactions
                scrollToDate(dateKey);
            });

            calendarDays.appendChild(dayCell);
        }
    }

    // Render transactions with swipe actions
    function renderLichTransactions() {
        const transactionsList = document.getElementById('lich-transactions-list');
        if (!transactionsList || !lichData) return;

        transactionsList.innerHTML = '';

        lichData.transactions_by_date.forEach(dateGroup => {
            const groupDiv = document.createElement('div');
            groupDiv.className = 'chi-lich-transaction-group';
            groupDiv.setAttribute('data-date', dateGroup.date);

            const dateDiv = document.createElement('div');
            dateDiv.className = 'chi-lich-transaction-date';
            const totals = lichData.daily_totals[dateGroup.date] || { thu: 0, chi: 0 };
            const dayTotal = totals.thu - totals.chi;

            dateDiv.innerHTML = `
                    ${dateGroup.date} (${dateGroup.day_name})
                    ${dayTotal !== 0 ? `<span class="chi-lich-day-total ${dayTotal < 0 ? 'negative' : 'positive'}">${dayTotal.toLocaleString('vi-VN')}₫</span>` : ''}
                `;
            groupDiv.appendChild(dateDiv);

            dateGroup.transactions.forEach(trans => {
                // Wrapper cho swipe
                const swipeWrapper = document.createElement('div');
                swipeWrapper.className = 'swipe-wrapper';

                const itemDiv = document.createElement('div');
                itemDiv.className = 'chi-lich-transaction-item swipeable';
                itemDiv.setAttribute('data-row-id', trans.row_id);

                let colorClass = trans.loai;
                if (trans.danh_muc === 'Thu quỹ') {
                    colorClass = 'chi';
                } else if (trans.danh_muc === 'Chi quỹ') {
                    colorClass = 'chi';
                }

                let categoryDisplay = trans.danh_muc;
                if ((trans.danh_muc === 'Thu quỹ' || trans.danh_muc === 'Chi quỹ') && trans.quy && trans.quy.trim() && trans.quy.toLowerCase() !== 'nan') {
                    categoryDisplay = trans.quy.trim();
                }

                itemDiv.innerHTML = `
                        <div class="chi-lich-transaction-details">
                            <div class="chi-lich-transaction-category">
                                ${categoryDisplay}
                                ${(trans.danh_muc === 'Thu quỹ' || trans.danh_muc === 'Chi quỹ') && trans.quy && trans.quy.trim() && trans.quy.toLowerCase() !== 'nan'
                        ? `<span class="chi-lich-fund-badge">${trans.danh_muc}</span>`
                        : ''}
                            </div>
                            ${trans.ghi_chu && trans.ghi_chu.trim() && trans.ghi_chu.toLowerCase() !== 'nan' ? `<div class="chi-lich-transaction-note">${trans.ghi_chu}</div>` : ''}
                        </div>
                        <div class="chi-lich-transaction-amount ${colorClass}">${trans.so_tien.toLocaleString('vi-VN')}₫</div>
                    `;

                // Actions panel (hiện khi swipe)
                const actionsDiv = document.createElement('div');
                actionsDiv.className = 'swipe-actions';
                actionsDiv.innerHTML = `
                            <button class="swipe-btn edit-btn" title="Sửa">✏️</button>
                            <button class="swipe-btn delete-btn" title="Xóa">🗑️</button>
                        `;

                swipeWrapper.appendChild(itemDiv);
                swipeWrapper.appendChild(actionsDiv);

                // Xử lý swipe
                let startX = 0;
                let currentX = 0;
                let isDragging = false;
                let startTranslate = 0;

                itemDiv.addEventListener('touchstart', (e) => {
                    startX = e.touches[0].clientX;
                    currentX = startX;
                    isDragging = true;
                    itemDiv.style.transition = 'none';
                    startTranslate = swipeWrapper.classList.contains('swiped') ? -120 : 0;
                });

                itemDiv.addEventListener('touchmove', (e) => {
                    if (!isDragging) return;
                    currentX = e.touches[0].clientX;
                    const diff = currentX - startX;
                    let newTranslate = startTranslate + diff;

                    // Limit boundaries
                    if (newTranslate > 0) newTranslate = 0;
                    if (newTranslate < -150) newTranslate = -150;

                    itemDiv.style.transform = `translateX(${newTranslate}px)`;
                });

                itemDiv.addEventListener('touchend', () => {
                    if (!isDragging) return;
                    isDragging = false;
                    itemDiv.style.transition = 'transform 0.3s ease';

                    const diff = currentX - startX;
                    const openThreshold = 40;
                    const closeThreshold = 15;

                    if (startTranslate === 0) {
                        // Opening
                        if (diff < -openThreshold) {
                            itemDiv.style.transform = 'translateX(-120px)';
                            swipeWrapper.classList.add('swiped');
                        } else {
                            itemDiv.style.transform = 'translateX(0)';
                            swipeWrapper.classList.remove('swiped');
                        }
                    } else {
                        // Closing
                        if (diff > closeThreshold) {
                            itemDiv.style.transform = 'translateX(0)';
                            swipeWrapper.classList.remove('swiped');
                        } else {
                            itemDiv.style.transform = 'translateX(-120px)';
                            swipeWrapper.classList.add('swiped');
                        }
                    }
                });

                // Click để đóng nếu đã mở
                itemDiv.addEventListener('click', () => {
                    if (swipeWrapper.classList.contains('swiped')) {
                        itemDiv.style.transform = 'translateX(0)';
                        swipeWrapper.classList.remove('swiped');
                    }
                });

                // Xử lý nút Edit
                actionsDiv.querySelector('.edit-btn').addEventListener('click', () => {
                    openEditTransactionModal(trans);
                });

                // Xử lý nút Delete
                actionsDiv.querySelector('.delete-btn').addEventListener('click', () => {
                    if (confirm(`Xóa giao dịch "${categoryDisplay}" - ${trans.so_tien.toLocaleString('vi-VN')}₫?`)) {
                        deleteTransaction(trans.row_id);
                    }
                });

                groupDiv.appendChild(swipeWrapper);
            });

            transactionsList.appendChild(groupDiv);
        });
    }

    // Update summary
    function updateLichSummary() {
        if (!lichData) return;
        const summary = lichData.monthly_summary;
        document.getElementById('lich-summary-thu').textContent = summary.thu.toLocaleString('vi-VN') + '₫';
        document.getElementById('lich-summary-chi').textContent = summary.chi.toLocaleString('vi-VN') + '₫';
        const tong = document.getElementById('lich-summary-tong');
        tong.textContent = summary.tong.toLocaleString('vi-VN') + '₫';
        tong.classList.toggle('negative', summary.tong < 0);
    }

    // Delete transaction function
    async function deleteTransaction(rowId) {
        try {
            const res = await fetch(`/api/expenses/${rowId}`, {
                method: 'DELETE'
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Xóa thất bại');

            alert('Đã xóa giao dịch thành công!');
            // Reload calendar data
            lichData = null;
            loadLichData(true).then(data => {
                if (data) {
                    renderLichCalendar();
                    renderLichTransactions();
                    updateLichSummary();
                }
            });
        } catch (err) {
            alert('Lỗi: ' + err.message);
            console.error('Delete error:', err);
        }
    }

    // Open edit transaction modal
    function openEditTransactionModal(trans) {
        // Tạo modal
        const modal = document.createElement('div');
        modal.className = 'edit-transaction-modal';
        modal.innerHTML = `
                    <div class="edit-transaction-content">
                        <h3>✏️ Sửa giao dịch</h3>
                        <div class="chi-field">
                            <label>Ngày</label>
                            <input type="text" class="chi-input" id="edit-trans-ngay" value="${trans.ngay}" readonly>
                        </div>
                        <div class="chi-field">
                            <label>Loại</label>
                            <select class="chi-input" id="edit-trans-loai">
                                <option value="thu" ${trans.loai === 'thu' ? 'selected' : ''}>Thu</option>
                                <option value="chi" ${trans.loai === 'chi' ? 'selected' : ''}>Chi</option>
                            </select>
                        </div>
                        <div class="chi-field">
                            <label>Danh mục</label>
                            <input type="text" class="chi-input" id="edit-trans-danh-muc" value="${trans.danh_muc}">
                        </div>
                        <div class="chi-field">
                            <label>Số tiền</label>
                            <input type="number" class="chi-input" id="edit-trans-so-tien" value="${trans.so_tien}">
                        </div>
                        <div class="chi-field">
                            <label>Ghi chú</label>
                            <input type="text" class="chi-input" id="edit-trans-ghi-chu" value="${trans.ghi_chu || ''}">
                        </div>
                        <div class="chi-field">
                            <label>Quỹ</label>
                            <input type="text" class="chi-input" id="edit-trans-quy" value="${trans.quy || ''}">
                        </div>
                        <div class="edit-transaction-actions">
                            <button type="button" class="cancel-btn">Hủy</button>
                            <button type="button" class="save-btn">Lưu</button>
                        </div>
                    </div>
                `;

        document.body.appendChild(modal);

        // Xử lý nút Hủy
        modal.querySelector('.cancel-btn').addEventListener('click', () => {
            modal.remove();
        });

        // Đóng khi click overlay
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });

        // Xử lý nút Lưu
        modal.querySelector('.save-btn').addEventListener('click', async () => {
            const updatedTrans = {
                ngay: document.getElementById('edit-trans-ngay').value,
                loai: document.getElementById('edit-trans-loai').value,
                danh_muc: document.getElementById('edit-trans-danh-muc').value,
                so_tien: parseFloat(document.getElementById('edit-trans-so-tien').value),
                ghi_chu: document.getElementById('edit-trans-ghi-chu').value,
                quy: document.getElementById('edit-trans-quy').value
            };

            try {
                const res = await fetch(`/api/expenses/${trans.row_id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(updatedTrans)
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.error || 'Cập nhật thất bại');

                alert('Đã cập nhật giao dịch!');
                modal.remove();

                // Reload calendar
                lichData = null;
                loadLichData(true).then(data => {
                    if (data) {
                        renderLichCalendar();
                        renderLichTransactions();
                        updateLichSummary();
                    }
                });
            } catch (err) {
                alert('Lỗi: ' + err.message);
                console.error('Update error:', err);
            }
        });
    }

    function formatDateKey(date) {
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        return `${day}/${month}/${year}`;
    }

    function scrollToDate(dateKey) {
        const group = document.querySelector(`[data-date="${dateKey}"]`);
        if (group) {
            // Remove highlight from all groups
            document.querySelectorAll('.chi-lich-transaction-group').forEach(g => g.classList.remove('highlighted'));
            // Add highlight to selected group
            group.classList.add('highlighted');
            // Scroll to group
            group.scrollIntoView({ behavior: 'smooth', block: 'start' });
            // Remove highlight after 2 seconds
            setTimeout(() => {
                group.classList.remove('highlighted');
            }, 2000);
        } else {
            // Nếu không có giao dịch, không làm gì
        }
    }    // Báo cáo
    let reportChart = null;
    let reportMonthlyChart = null;

    function formatNumber(n) {
        try { return Number(n).toLocaleString('vi-VN'); } catch { return n; }
    }

    async function loadReport() {
        const wrap = document.getElementById('report-years');
        const chartEl = document.getElementById('report-chart');
        const wrapMonths = document.getElementById('report-months');
        const chartElMonths = document.getElementById('report-chart-monthly');
        if (!chartEl) return;
        if (wrap) wrap.innerHTML = '<div class="chi-cat placeholder">Đang tải...</div>';
        if (wrapMonths) wrapMonths.innerHTML = '<div class="chi-cat placeholder">Đang tải...</div>';
        try {
            const res = await fetch('/api/user_yearly_report?years=5');
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Không tải được báo cáo');
            const items = data.years || [];
            if (!items.length) {
                if (wrap) wrap.innerHTML = '<div class="chi-cat placeholder">Không có dữ liệu</div>';
                return;
            }
            // render chart (income as line, expense & fund as bars)
            if (chartEl && window.Chart) {
                const labels = items.map(i => i.year);
                const incomes = items.map(i => i.income || 0);
                const expenses = items.map(i => i.expense || 0);
                const funds = items.map(i => i.fund || 0);
                chartEl.parentElement.style.height = `${Math.max(260, labels.length * 55)}px`;
                if (reportChart) reportChart.destroy();
                reportChart = new Chart(chartEl, {
                    type: 'bar',
                    data: {
                        labels,
                        datasets: [
                            {
                                label: 'Thu',
                                data: incomes,
                                type: 'line',
                                borderColor: '#4ade80',
                                backgroundColor: 'rgba(74,222,128,0.18)',
                                borderWidth: 3,
                                tension: 0.25,
                                fill: false,
                                pointRadius: 5,
                                pointBackgroundColor: '#22c55e'
                            },
                            { label: 'Chi', data: expenses, backgroundColor: 'rgba(239,68,68,0.8)', borderRadius: 10, barThickness: 26, maxBarThickness: 32, stack: 'stack' },
                            {
                                label: 'Quỹ',
                                data: funds,
                                type: 'line',
                                borderColor: '#3b82f6',
                                backgroundColor: 'rgba(59,130,246,0.18)',
                                borderWidth: 3,
                                tension: 0.25,
                                fill: false,
                                pointRadius: 5,
                                pointBackgroundColor: '#3b82f6'
                            },
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    color: '#e2e8f0',
                                    callback: (v) => formatNumber(v)
                                },
                                grid: { color: 'rgba(148,163,184,0.25)' },
                                border: { color: 'rgba(148,163,184,0.35)' }
                            },
                            x: {
                                ticks: {
                                    color: '#e2e8f0',
                                    callback: (_val, idx) => labels[idx] ?? _val
                                },
                                grid: { color: 'rgba(148,163,184,0.18)' },
                                border: { color: 'rgba(148,163,184,0.35)' }
                            }
                        },
                        plugins: {
                            legend: {
                                position: 'top',
                                labels: { usePointStyle: true, boxWidth: 10, boxHeight: 10, color: '#e5e7eb' }
                            },
                            tooltip: {
                                backgroundColor: 'rgba(15,23,42,0.9)',
                                titleColor: '#e5e7eb',
                                bodyColor: '#e5e7eb',
                                callbacks: {
                                    label: (ctx) => {
                                        const val = ctx.parsed.y ?? ctx.parsed.x;
                                        return `${ctx.dataset.label}: ${formatNumber(val)}`;
                                    }
                                }
                            }
                        }
                    }
                });
            }

            // Render bar chart below (optional, skip if wrap doesn't exist)
            if (wrap) {
                const maxVal = Math.max(...items.map(i => Math.max(i.income || 0, i.expense || 0, i.fund || 0, 1)));
                wrap.innerHTML = items.map(i => {
                    const incW = Math.round((i.income || 0) / maxVal * 100);
                    const expW = Math.round((i.expense || 0) / maxVal * 100);
                    const fundW = Math.round((i.fund || 0) / maxVal * 100);
                    return `
                <div class="report-row">
                    <div class="report-year">${i.year}</div>
                    <div class="report-bars">
                        <div class="bar income" style="width:${incW}%">
                            <span>${formatNumber(i.income || 0)}</span>
                        </div>
                        <div class="bar expense" style="width:${expW}%">
                            <span>${formatNumber(i.expense || 0)}</span>
                        </div>
                        <div class="bar fund" style="width:${fundW}%">
                            <span>${formatNumber(i.fund || 0)}</span>
                        </div>
                    </div>
                </div>`;
                }).join('');
            }

            // Monthly report (current year)
            if (chartElMonths && window.Chart) {
                const resMonth = await fetch('/api/user_monthly_report');
                const dataMonth = await resMonth.json();
                if (!resMonth.ok) throw new Error(dataMonth.error || 'Không tải được báo cáo tháng');
                const months = dataMonth.months || [];
                if (!months.length) {
                    if (wrapMonths) wrapMonths.innerHTML = '<div class="chi-cat placeholder">Không có dữ liệu</div>';
                } else {
                    if (wrapMonths) wrapMonths.innerHTML = '';
                }
                const labelsM = months.map(m => `T${m.month}`);
                const incomesM = months.map(m => m.income || 0);
                const expensesM = months.map(m => m.expense || 0);
                const fundsM = months.map(m => m.fund || 0);
                chartElMonths.parentElement.style.height = `${Math.max(260, labelsM.length * 55)}px`;
                if (reportMonthlyChart) reportMonthlyChart.destroy();
                reportMonthlyChart = new Chart(chartElMonths, {
                    type: 'bar',
                    data: {
                        labels: labelsM,
                        datasets: [
                            {
                                label: 'Thu',
                                data: incomesM,
                                type: 'line',
                                borderColor: '#4ade80',
                                backgroundColor: 'rgba(74,222,128,0.18)',
                                borderWidth: 3,
                                tension: 0.25,
                                fill: false,
                                pointRadius: 5,
                                pointBackgroundColor: '#22c55e'
                            },
                            {
                                label: 'Chi',
                                data: expensesM,
                                backgroundColor: 'rgba(239,68,68,0.8)',
                                borderRadius: 10,
                                barThickness: 26,
                                maxBarThickness: 32,
                                stack: 'stack'
                            },
                            {
                                label: 'Quỹ',
                                data: fundsM,
                                type: 'line',
                                borderColor: '#3b82f6',
                                backgroundColor: 'rgba(59,130,246,0.18)',
                                borderWidth: 3,
                                tension: 0.25,
                                fill: false,
                                pointRadius: 5,
                                pointBackgroundColor: '#3b82f6'
                            },
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    color: '#e2e8f0',
                                    callback: (v) => formatNumber(v)
                                },
                                grid: { color: 'rgba(148,163,184,0.25)' },
                                border: { color: 'rgba(148,163,184,0.35)' }
                            },
                            x: {
                                ticks: {
                                    color: '#e2e8f0',
                                    callback: (_val, idx) => labelsM[idx] ?? _val
                                },
                                grid: { color: 'rgba(148,163,184,0.18)' },
                                border: { color: 'rgba(148,163,184,0.35)' }
                            }
                        },
                        plugins: {
                            legend: {
                                position: 'top',
                                labels: { usePointStyle: true, boxWidth: 10, boxHeight: 10, color: '#e5e7eb' }
                            },
                            tooltip: {
                                backgroundColor: 'rgba(15,23,42,0.9)',
                                titleColor: '#e5e7eb',
                                bodyColor: '#e5e7eb',
                                callbacks: {
                                    label: (ctx) => {
                                        const val = ctx.parsed.y ?? ctx.parsed.x;
                                        return `${ctx.dataset.label}: ${formatNumber(val)}`;
                                    }
                                }
                            }
                        }
                    }
                });
            }
        } catch (err) {
            if (wrap) wrap.innerHTML = `<div class="chi-cat placeholder" style="color:#ef4444;">${err.message}</div>`;
            if (wrapMonths) wrapMonths.innerHTML = `<div class="chi-cat placeholder" style="color:#ef4444;">${err.message}</div>`;
        }
    }
    let reportDailyChart = null;

    async function loadDailyReport() {
        const chartEl = document.getElementById('report-chart-daily');
        const label = document.getElementById('daily-chart-label');
        if (!chartEl || !window.Chart) return;

        try {
            const res = await fetch('/api/user_daily_report');
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Không tải được báo cáo ngày');

            const days = data.days || [];
            const month = data.month;
            const year = data.year;

            if (label) {
                label.textContent = `Báo cáo ngày trong tháng ${month}/${year} (Thu / Chi / Quỹ)`;
            }

            if (!days.length) return;

            const labels = days.map(d => d.day);
            const incomes = days.map(d => d.income || 0);
            const expenses = days.map(d => d.expense || 0);
            const funds = days.map(d => d.fund || 0);

            chartEl.parentElement.style.height = '300px';
            if (reportDailyChart) reportDailyChart.destroy();
            reportDailyChart = new Chart(chartEl, {
                type: 'bar',
                data: {
                    labels,
                    datasets: [
                        {
                            label: 'Thu',
                            data: incomes,
                            type: 'line',
                            borderColor: '#4ade80',
                            backgroundColor: 'rgba(74,222,128,0.18)',
                            borderWidth: 2,
                            tension: 0.25,
                            fill: false,
                            pointRadius: 3,
                            pointBackgroundColor: '#22c55e'
                        },
                        {
                            label: 'Chi',
                            data: expenses,
                            backgroundColor: 'rgba(239,68,68,0.8)',
                            borderRadius: 6,
                            barThickness: 12,
                            maxBarThickness: 16
                        },
                        {
                            label: 'Quỹ',
                            data: funds,
                            type: 'line',
                            borderColor: '#3b82f6',
                            backgroundColor: 'rgba(59,130,246,0.18)',
                            borderWidth: 2,
                            tension: 0.25,
                            fill: false,
                            pointRadius: 3,
                            pointBackgroundColor: '#3b82f6'
                        },
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                color: '#e2e8f0',
                                callback: (v) => formatNumber(v)
                            },
                            grid: { color: 'rgba(148,163,184,0.25)' },
                            border: { color: 'rgba(148,163,184,0.35)' }
                        },
                        x: {
                            ticks: { color: '#e2e8f0' },
                            grid: { color: 'rgba(148,163,184,0.18)' },
                            border: { color: 'rgba(148,163,184,0.35)' }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: { usePointStyle: true, boxWidth: 10, boxHeight: 10, color: '#e5e7eb' }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(15,23,42,0.9)',
                            titleColor: '#e5e7eb',
                            bodyColor: '#e5e7eb',
                            callbacks: {
                                label: (ctx) => {
                                    const val = ctx.parsed.y ?? ctx.parsed.x;
                                    return `${ctx.dataset.label}: ${formatNumber(val)}`;
                                }
                            }
                        }
                    }
                }
            });
        } catch (err) {
            console.error('Error loading daily report:', err);
        }
    }
    let reportCategoryChart = null;

    async function loadCategoryReport() {
        const chartEl = document.getElementById('report-chart-category');
        const label = document.getElementById('category-chart-label');
        if (!chartEl || !window.Chart) return;

        try {
            const res = await fetch('/api/user_category_breakdown');
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Không tải được phân bổ danh mục');

            const categories = data.categories || [];
            const month = data.month;
            const year = data.year;
            const backgroundColors = [
                '#ef4444', '#f97316', '#f59e0b', '#84cc16', '#10b981',
                '#06b6d4', '#3b82f6', '#6366f1', '#8b5cf6', '#d946ef',
                '#f43f5e', '#64748b'
            ];

            const labels = categories.map(c => c.name);
            const amounts = categories.map(c => c.amount);

            if (reportCategoryChart) reportCategoryChart.destroy();

            reportCategoryChart = new Chart(chartEl, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: amounts,
                        backgroundColor: backgroundColors,
                        borderWidth: 0,
                        hoverOffset: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                color: '#e2e8f0',
                                usePointStyle: true,
                                padding: 20,
                                font: { size: 12 }
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(15,23,42,0.9)',
                            titleColor: '#e5e7eb',
                            bodyColor: '#e5e7eb',
                            callbacks: {
                                label: (ctx) => {
                                    const val = ctx.parsed;
                                    const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((val / total) * 100).toFixed(1) + '%';
                                    return `${ctx.label}: ${formatNumber(val)} (${percentage})`;
                                }
                            }
                        }
                    },
                    layout: {
                        padding: 20
                    }
                }
            });

        } catch (err) {
            console.error('Error loading category report:', err);
        }
    }





    // Switch view


    // Switch view
    const baoCaoSection = document.getElementById('bao-cao-section');
    const menuSection = document.getElementById('menu-section');
    const navBaoCao = document.getElementById('nav-bao-cao');
    const navMenu = document.querySelector('.chi-bottom-item:last-child');
    const chiTabs = document.querySelector('.chi-tabs');

    function switchView(view) {
        if (view === 'form') {
            formSection.style.display = 'block';
            lichSection.style.display = 'none';
            if (baoCaoSection) baoCaoSection.style.display = 'none';
            if (menuSection) menuSection.style.display = 'none';
            navNhapVao.classList.add('active');
            navLich.classList.remove('active');
            if (navBaoCao) navBaoCao.classList.remove('active');
            if (navMenu) navMenu.classList.remove('active');
            // Hiện lại tabs khi ở form
            if (chiTabs) {
                chiTabs.style.display = 'grid';
            }
        } else if (view === 'lich') {
            formSection.style.display = 'none';
            lichSection.style.display = 'block';
            if (baoCaoSection) baoCaoSection.style.display = 'none';
            if (menuSection) menuSection.style.display = 'none';
            navNhapVao.classList.remove('active');
            navLich.classList.add('active');
            if (navBaoCao) navBaoCao.classList.remove('active');
            if (navMenu) navMenu.classList.remove('active');
            // Ẩn tabs khi ở lịch
            if (chiTabs) {
                chiTabs.style.display = 'none';
            }

            // Load và render lịch (force reload để lấy dữ liệu mới nhất)
            lichData = null; // Reset để reload dữ liệu mới
            loadLichData(true).then(data => {
                if (data) {
                    renderLichCalendar();
                    renderLichTransactions();
                    updateLichSummary();
                }
            });
        } else if (view === 'bao-cao') {
            formSection.style.display = 'none';
            lichSection.style.display = 'none';
            if (baoCaoSection) baoCaoSection.style.display = 'block';
            if (menuSection) menuSection.style.display = 'none';
            navNhapVao.classList.remove('active');
            navLich.classList.remove('active');
            if (navBaoCao) navBaoCao.classList.add('active');
            if (navMenu) navMenu.classList.remove('active');
            // Ẩn tabs khi ở báo cáo
            if (chiTabs) {
                chiTabs.style.display = 'none';
            }

            // Load báo cáo
            loadReport();
            loadDailyReport();
            loadCategoryReport();
        } else if (view === 'menu') {
            formSection.style.display = 'none';
            lichSection.style.display = 'none';
            if (baoCaoSection) baoCaoSection.style.display = 'none';
            if (menuSection) menuSection.style.display = 'block';
            navNhapVao.classList.remove('active');
            navLich.classList.remove('active');
            if (navBaoCao) navBaoCao.classList.remove('active');
            if (navMenu) navMenu.classList.add('active');
            // Ẩn tabs khi ở menu
            if (chiTabs) {
                chiTabs.style.display = 'none';
            }
            // Load icons khi vào menu
            loadIcons();
            // Load danh sách danh mục
            if (typeof loadCategoryList === 'function') {
                loadCategoryList();
            }
        }
    }

    navNhapVao.addEventListener('click', () => switchView('form'));
    navLich.addEventListener('click', () => switchView('lich'));
    if (navBaoCao) {
        navBaoCao.addEventListener('click', () => switchView('bao-cao'));
    }
    if (navMenu) {
        navMenu.addEventListener('click', () => switchView('menu'));
    }

    // Load icons và xử lý icon picker (datalist)
    let selectedIcon = '';
    const iconPickerInput = document.getElementById('icon-picker-input');
    const iconList = document.getElementById('icon-list');

    async function loadIcons() {
        try {
            const response = await fetch('/api/icons');
            const data = await response.json();

            if (data.icons && data.icons.length > 0 && iconList) {
                // Xóa tất cả options
                iconList.innerHTML = '';

                // Thêm các icon vào datalist
                data.icons.forEach(icon => {
                    const option = document.createElement('option');
                    option.value = icon;
                    iconList.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Lỗi khi load icons:', error);
        }
    }

    // Load icons khi vào menu
    if (iconList) {
        loadIcons();
    }

    if (iconPickerInput) {
        iconPickerInput.addEventListener('change', (e) => {
            selectedIcon = e.target.value.trim();
        });
        iconPickerInput.addEventListener('input', (e) => {
            selectedIcon = e.target.value.trim();
        });
    }

    // Xử lý submit form tạo danh mục
    const categoryForm = document.getElementById('category-form');
    if (categoryForm) {
        categoryForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const categoryName = document.getElementById('category-name').value.trim();
            const categoryType = document.getElementById('category-type').value;

            if (!categoryName) {
                alert('Vui lòng nhập tên danh mục');
                return;
            }

            try {
                const response = await fetch('/api/categories', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        name: categoryName,
                        type: categoryType,
                        icon: document.getElementById('icon-picker-input').value.trim()
                    })
                });

                const data = await response.json();

                if (data.success) {
                    alert(data.message);
                    // Reset form
                    categoryForm.reset();
                    document.getElementById('category-type').value = 'Chi';
                    selectedIcon = '';
                    if (iconPickerInput) {
                        iconPickerInput.value = '';
                    }

                    // Reload danh sách danh mục nếu đang ở tab tương ứng
                    if (currentType === categoryType ||
                        (currentType === 'Chi' && categoryType === 'Chi') ||
                        (currentType === 'Thu' && categoryType === 'Thu') ||
                        (currentType === 'ThuQuy' && categoryType === 'ThuQuy') ||
                        (currentType === 'ChiQuy' && categoryType === 'ChiQuy')) {
                        if (currentType === 'ThuQuy') {
                            loadQuyPurposesThu();
                        } else if (currentType === 'ChiQuy') {
                            loadQuyPurposesChi();
                        } else {
                            loadCategories(currentType);
                        }
                    }

                    // Reload danh sách quản lý danh mục (nếu đang ở trang menu)
                    if (typeof loadCategoryList === 'function') {
                        loadCategoryList();
                    }
                } else {
                    alert('Lỗi: ' + (data.error || 'Không thể tạo danh mục'));
                }
            } catch (error) {
                console.error('Lỗi khi tạo danh mục:', error);
                alert('Lỗi: ' + error.message);
            }
        });
    }

    // Load danh sách danh mục để quản lý
    const categoryListType = document.getElementById('category-list-type');
    const categoryListContainer = document.getElementById('category-list-container');
    let editSelectedIcon = '';

    async function loadCategoryList() {
        if (!categoryListType || !categoryListContainer) return;

        const type = categoryListType.value;
        categoryListContainer.innerHTML = '<div class="chi-cat placeholder">Đang tải...</div>';

        try {
            const response = await fetch(`/api/categories/${type}`);
            const data = await response.json();

            if (data.categories && data.categories.length > 0) {
                categoryListContainer.innerHTML = '';
                data.categories.forEach(cat => {
                    const catItem = document.createElement('div');
                    catItem.className = 'category-item';
                    catItem.style.cssText = 'display: flex; align-items: center; justify-content: space-between; padding: 0.75rem; border-radius: 0.75rem; margin-bottom: 0.5rem;';

                    const catInfo = document.createElement('div');
                    catInfo.className = 'category-item-info';
                    catInfo.style.cssText = 'display: flex; align-items: center; gap: 0.5rem; font-weight: 600;';
                    catInfo.textContent = cat.value;

                    const catActions = document.createElement('div');
                    catActions.style.cssText = 'display: flex; gap: 0.5rem;';

                    const editBtn = document.createElement('button');
                    editBtn.textContent = '✏️ Sửa';
                    editBtn.className = 'chi-btn-cancel';
                    editBtn.style.cssText = 'padding: 0.5rem 1rem; font-size: 0.9rem; border: 1px solid #e5e7eb;';
                    editBtn.onclick = () => editCategory(cat, type);

                    const deleteBtn = document.createElement('button');
                    deleteBtn.textContent = '🗑️ Xóa';
                    deleteBtn.className = 'chi-btn-cancel chi-btn-delete';
                    deleteBtn.style.cssText = 'padding: 0.5rem 1rem; font-size: 0.9rem; border: 1px solid #fca5a5;';
                    deleteBtn.onclick = () => deleteCategory(cat, type);

                    catActions.appendChild(editBtn);
                    catActions.appendChild(deleteBtn);

                    catItem.appendChild(catInfo);
                    catItem.appendChild(catActions);
                    categoryListContainer.appendChild(catItem);
                });
            } else {
                categoryListContainer.innerHTML = '<div class="chi-cat placeholder">Không có danh mục</div>';
            }
        } catch (error) {
            console.error('Lỗi khi load danh sách danh mục:', error);
            categoryListContainer.innerHTML = '<div class="chi-cat placeholder" style="color:#ef4444;">Lỗi khi tải danh sách</div>';
        }
    }

    if (categoryListType) {
        categoryListType.addEventListener('change', loadCategoryList);
    }

    // Hàm sửa danh mục
    function editCategory(cat, type) {
        const modal = document.getElementById('edit-category-modal');
        const form = document.getElementById('edit-category-form');

        // Parse icon và tên từ value
        const value = cat.value;
        let icon = '';
        let name = value;
        const match = value.match(/^([^\w\s]+)\s+(.+)$/);
        if (match) {
            icon = match[1];
            name = match[2];
        }

        document.getElementById('edit-category-row').value = cat.row;
        document.getElementById('edit-category-type').value = type;
        document.getElementById('edit-category-column').value = cat.column || '';
        document.getElementById('edit-category-old-value').value = cat.value;
        document.getElementById('edit-category-name').value = name;

        // Set icon trong input
        const editIconInput = document.getElementById('edit-icon-picker-input');
        if (editIconInput) {
            editIconInput.value = icon || '';
            editSelectedIcon = icon;
        }

        if (modal) {
            modal.style.display = 'flex';
        }
    }

    // Hàm xóa danh mục
    async function deleteCategory(cat, type) {
        if (!confirm(`Bạn có chắc chắn muốn xóa danh mục "${cat.value}"?`)) {
            return;
        }

        try {
            const response = await fetch('/api/categories', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    type: type,
                    row: cat.row,
                    value: cat.value,
                    column: cat.column || ''
                })
            });

            const data = await response.json();

            if (data.success) {
                alert(data.message);
                loadCategoryList();
                // Reload danh sách trong form nếu đang ở tab tương ứng
                if (currentType === type ||
                    (currentType === 'Chi' && type === 'Chi') ||
                    (currentType === 'Thu' && type === 'Thu') ||
                    ((currentType === 'ThuQuy' || currentType === 'ChiQuy') && type === 'Quy')) {
                    if (currentType === 'ThuQuy') {
                        loadQuyPurposesThu();
                    } else if (currentType === 'ChiQuy') {
                        loadQuyPurposesChi();
                    } else {
                        loadCategories(currentType);
                    }
                }
            } else {
                alert('Lỗi: ' + (data.error || 'Không thể xóa danh mục'));
            }
        } catch (error) {
            console.error('Lỗi khi xóa danh mục:', error);
            alert('Lỗi: ' + error.message);
        }
    }

    // Load icons cho edit modal (datalist dùng chung icon-list)
    const editIconInput = document.getElementById('edit-icon-picker-input');

    if (editIconInput) {
        editIconInput.addEventListener('change', (e) => {
            editSelectedIcon = e.target.value.trim();
        });
        editIconInput.addEventListener('input', (e) => {
            editSelectedIcon = e.target.value.trim();
        });
    }

    // Xử lý form sửa danh mục
    const editCategoryForm = document.getElementById('edit-category-form');
    const editCategoryModal = document.getElementById('edit-category-modal');
    const editCategoryClose = document.getElementById('edit-category-close');
    const editCategoryCancel = document.getElementById('edit-category-cancel');

    if (editCategoryForm) {
        editCategoryForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const newName = document.getElementById('edit-category-name').value.trim();
            const row = document.getElementById('edit-category-row').value;
            const type = document.getElementById('edit-category-type').value;
            const column = document.getElementById('edit-category-column').value;
            const oldValue = document.getElementById('edit-category-old-value').value;

            if (!newName) {
                alert('Vui lòng nhập tên danh mục');
                return;
            }

            try {
                const response = await fetch('/api/categories', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        type: type,
                        row: parseInt(row),
                        old_value: oldValue,
                        name: newName,
                        icon: editIconInput ? editIconInput.value.trim() : editSelectedIcon,
                        column: column
                    })
                });

                const data = await response.json();

                if (data.success) {
                    alert(data.message);
                    if (editCategoryModal) {
                        editCategoryModal.style.display = 'none';
                    }
                    loadCategoryList();
                    // Reload danh sách trong form
                    if (currentType === type ||
                        (currentType === 'Chi' && type === 'Chi') ||
                        (currentType === 'Thu' && type === 'Thu') ||
                        ((currentType === 'ThuQuy' || currentType === 'ChiQuy') && type === 'Quy')) {
                        if (currentType === 'ThuQuy') {
                            loadQuyPurposesThu();
                        } else if (currentType === 'ChiQuy') {
                            loadQuyPurposesChi();
                        } else {
                            loadCategories(currentType);
                        }
                    }
                } else {
                    alert('Lỗi: ' + (data.error || 'Không thể sửa danh mục'));
                }
            } catch (error) {
                console.error('Lỗi khi sửa danh mục:', error);
                alert('Lỗi: ' + error.message);
            }
        });
    }

    if (editCategoryClose) {
        editCategoryClose.addEventListener('click', () => {
            if (editCategoryModal) editCategoryModal.style.display = 'none';
        });
    }

    if (editCategoryCancel) {
        editCategoryCancel.addEventListener('click', () => {
            if (editCategoryModal) editCategoryModal.style.display = 'none';
        });
    }

    if (editCategoryModal) {
        editCategoryModal.addEventListener('click', (e) => {
            if (e.target === editCategoryModal) {
                editCategoryModal.style.display = 'none';
            }
        });
    }

    // Click vào tháng/năm để mở native month picker (giống sample)
    const lichMonthPicker = document.getElementById('lich-month-picker');
    const lichMonthYear = document.getElementById('lich-month-year');
    if (lichMonthPicker && lichMonthYear) {
        lichMonthYear.addEventListener('click', () => {
            // Set giá trị hiện tại
            const year = lichCurrentDate.getFullYear();
            const month = String(lichCurrentDate.getMonth() + 1).padStart(2, '0');
            lichMonthPicker.value = `${year}-${month}`;
            // Enable và trigger native picker (giống sample)
            lichMonthPicker.style.pointerEvents = 'auto';
            lichMonthPicker.style.opacity = 1e-6;
            lichMonthPicker.focus();
            if (lichMonthPicker.showPicker) {
                lichMonthPicker.showPicker();
            }
        });

        // Xử lý khi chọn tháng/năm từ native picker
        lichMonthPicker.addEventListener('change', () => {
            const val = lichMonthPicker.value; // yyyy-mm
            if (!val) return;
            const [y, m] = val.split('-').map(Number);
            if (!y || !m) return;
            lichCurrentDate = new Date(y, m - 1, 1);
            lichData = null;
            // Reset picker style
            lichMonthPicker.style.pointerEvents = 'none';
            lichMonthPicker.style.opacity = 0;
            // Cập nhật lịch với tháng/năm đã chọn
            if (lichSection && lichSection.style.display !== 'none') {
                loadLichData(true).then(data => {
                    if (data) {
                        renderLichCalendar();
                        renderLichTransactions();
                        updateLichSummary();
                    }
                });
            }
        });
    }

    // Đóng popup khi click vào overlay
    document.getElementById('lich-popup-overlay')?.addEventListener('click', (e) => {
        if (e.target.id === 'lich-popup-overlay') {
            document.getElementById('lich-popup-overlay').style.display = 'none';
        }
    });

    // Render popup calendar
    function renderLichPopupCalendar() {
        const popupDays = document.getElementById('lich-popup-days');
        const popupMonthYear = document.getElementById('lich-popup-month-year');
        if (!popupDays || !popupMonthYear) return;

        const year = lichPopupDate.getFullYear();
        const month = lichPopupDate.getMonth();

        const monthNames = ['Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5', 'Tháng 6',
            'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12'];
        popupMonthYear.textContent = `${monthNames[month]} ${year}`;

        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const adjustedFirstDay = (firstDay === 0) ? 6 : firstDay - 1;

        popupDays.innerHTML = '';

        // Empty cells
        for (let i = 0; i < adjustedFirstDay; i++) {
            const emptyCell = document.createElement('div');
            emptyCell.className = 'chi-lich-popup-day empty';
            popupDays.appendChild(emptyCell);
        }

        // Days
        const today = new Date();
        for (let day = 1; day <= daysInMonth; day++) {
            const dayCell = document.createElement('div');
            dayCell.className = 'chi-lich-popup-day';

            const dateObj = new Date(year, month, day);
            const isToday = day === today.getDate() && month === today.getMonth() && year === today.getFullYear();
            const isSelectedMonth = month === lichCurrentDate.getMonth() && year === lichCurrentDate.getFullYear();

            // Highlight nếu đang xem tháng này
            if (isSelectedMonth) {
                dayCell.classList.add('selected');
            }
            if (isToday) {
                dayCell.classList.add('today');
            }

            dayCell.textContent = day;

            dayCell.addEventListener('click', () => {
                // Chọn tháng/năm này (không cần chọn ngày cụ thể)
                lichCurrentDate = new Date(year, month, 1);
                lichData = null;
                // Đóng popup
                document.getElementById('lich-popup-overlay').style.display = 'none';
                // Hiển thị lịch với tháng/năm đã chọn (không dùng switchView để tránh mở popup lại)
                formSection.style.display = 'none';
                lichSection.style.display = 'block';
                navNhapVao.classList.remove('active');
                navLich.classList.add('active');
                // Load và render lịch
                loadLichData(true).then(data => {
                    if (data) {
                        renderLichCalendar();
                        renderLichTransactions();
                        updateLichSummary();
                    }
                });
            });

            popupDays.appendChild(dayCell);
        }
    }

    // Popup navigation
    document.getElementById('lich-popup-prev-month')?.addEventListener('click', () => {
        lichPopupDate.setMonth(lichPopupDate.getMonth() - 1);
        renderLichPopupCalendar();
    });

    document.getElementById('lich-popup-next-month')?.addEventListener('click', () => {
        lichPopupDate.setMonth(lichPopupDate.getMonth() + 1);
        renderLichPopupCalendar();
    });

    // Calendar navigation
    document.getElementById('lich-prev-month')?.addEventListener('click', () => {
        lichCurrentDate.setMonth(lichCurrentDate.getMonth() - 1);
        lichData = null; // Reset để reload dữ liệu mới
        loadLichData(true).then(data => {
            if (data) {
                renderLichCalendar();
                renderLichTransactions();
                updateLichSummary();
            }
        });
    });

    document.getElementById('lich-next-month')?.addEventListener('click', () => {
        lichCurrentDate.setMonth(lichCurrentDate.getMonth() + 1);
        lichData = null; // Reset để reload dữ liệu mới
        loadLichData(true).then(data => {
            if (data) {
                renderLichCalendar();
                renderLichTransactions();
                updateLichSummary();
            }
        });
    });

}); // End DOMContentLoaded

// User dropdown
function toggleUserDropdown() {
    const dropdown = document.getElementById('userDropdown');
    dropdown.classList.toggle('show');
    document.querySelector('.user-profile-dropdown').classList.toggle('active');
}

// Close dropdown when clicking outside
window.addEventListener('click', function (event) {
    if (!event.target.matches('.user-profile-btn') && !event.target.closest('.user-profile-btn') && !event.target.closest('.user-dropdown-menu')) {
        const dropdown = document.getElementById('userDropdown');
        if (dropdown && dropdown.classList.contains('show')) {
            dropdown.classList.remove('show');
            document.querySelector('.user-profile-dropdown').classList.remove('active');
        }
    }
});