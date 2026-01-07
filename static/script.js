// Cập nhật thời gian khi trang được tải
document.addEventListener('DOMContentLoaded', function() {
    updateTime();
    
    // Tự động cập nhật thời gian mỗi giây
    setInterval(updateTime, 1000);
});

// Hàm cập nhật thời gian
async function updateTime() {
    try {
        const response = await fetch('/api/time');
        const data = await response.json();
        document.getElementById('time-display').textContent = 
            `${data.message} - ${data.time}`;
    } catch (error) {
        document.getElementById('time-display').textContent = 
            'Lỗi khi tải thời gian: ' + error.message;
    }
}

// Xử lý form gửi dữ liệu
document.getElementById('echo-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const input = document.getElementById('message-input');
    const message = input.value.trim();
    const responseDiv = document.getElementById('response');
    
    if (!message) {
        alert('Vui lòng nhập tin nhắn!');
        return;
    }
    
    try {
        const response = await fetch('/api/echo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        responseDiv.innerHTML = `
            <strong>Tin nhắn của bạn:</strong> ${data.received.message}<br>
            <strong>Phản hồi:</strong> ${data.message}
        `;
        responseDiv.classList.add('show');
        
        // Xóa input sau khi gửi
        input.value = '';
        
        // Ẩn response sau 5 giây
        setTimeout(() => {
            responseDiv.classList.remove('show');
        }, 5000);
        
    } catch (error) {
        responseDiv.innerHTML = `<strong>Lỗi:</strong> ${error.message}`;
        responseDiv.classList.add('show');
    }
});

