// frontend/chat.js
document.addEventListener('DOMContentLoaded', async () => {
    // 1. เชื่อมต่อกับ Socket.IO server ที่ Backend
    const socket = io.connect();

    // 2. ดึงข้อมูลจำเป็นจาก URL และ HTML
    const urlParams = new URLSearchParams(window.location.search);
    const productId = urlParams.get('product_id');
    const roomName = `product_${productId}`; // สร้างชื่อห้องแชท

    const chatMessagesContainer = document.querySelector('.chat-messages');
    const chatForm = document.querySelector('.chat-input-form');
    const messageInput = chatForm.querySelector('input');

    let currentUser = null;

    // --- ▼▼▼ ฟังก์ชันสำหรับแสดงข้อความในหน้าจอ ▼▼▼ ---
    function displayMessage(data) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');

        // ตรวจสอบว่าเป็นข้อความที่ "เราส่งเอง" หรือ "เราได้รับ"
        // (เปลี่ยนจากการเช็ค data.username เป็น data.sender_username ที่มาจาก DB)
        if (data.sender_username === currentUser.username) {
            messageDiv.classList.add('sent');
        } else {
            messageDiv.classList.add('received');
        }

        const timestamp = new Date(data.timestamp || new Date()).toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' });

        messageDiv.innerHTML = `
            <p>${data.message}</p>
            <span class="timestamp">${timestamp}</span>
        `;

        chatMessagesContainer.appendChild(messageDiv);
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    }
    // --- ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ ---


    // --- ▼▼▼ ฟังก์ชันสำหรับโหลดประวัติแชทจาก API ▼▼▼ ---
    async function loadChatHistory() {
        if (!roomName) return;
        try {
            const response = await fetch(`/api/chat/history/${roomName}`);
            if (response.ok) {
                const history = await response.json();
                // วนลูปแสดงผลข้อความเก่าทั้งหมด
                history.forEach(msgData => {
                    displayMessage(msgData);
                });
            } else {
                console.error('Could not fetch chat history.');
            }
        } catch (error) {
            console.error('Error fetching chat history:', error);
        }
    }
    // --- ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ ---


    // 3. ดึงข้อมูลผู้ใช้ที่ล็อกอินอยู่
    try {
        const response = await fetch('/api/check-auth', { credentials: 'include' });
        if (response.ok) {
            const data = await response.json();
            currentUser = data.user;
            // --- ▼▼▼ เรียกใช้ฟังก์ชันโหลดประวัติแชทหลังจากรู้ตัวตน user แล้ว ▼▼▼ ---
            await loadChatHistory();
        } else {
            throw new Error('User not authenticated');
        }
    } catch (error) {
        console.error('Authentication failed:', error);
        alert('กรุณาล็อกอินเพื่อใช้งานระบบแชท');
        window.location.href = 'User-Login.html';
        return;
    }

    // 4. เมื่อเชื่อมต่อกับ Server สำเร็จ ให้ "เข้าร่วมห้องแชท"
    socket.on('connect', () => {
        console.log('Connected to chat server!');
        socket.emit('join', { username: currentUser.username, room: roomName });
    });

    // 5. เมื่อมีการกดส่งข้อความในฟอร์ม
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const message = messageInput.value;
        if (message.trim()) {
            socket.emit('send_message', {
                username: currentUser.username, // ยังคงส่ง username ไปด้วยเพื่อให้ Socket ทำงานได้เหมือนเดิม
                message: message,
                room: roomName
            });
            messageInput.value = '';
        }
    });

    // 6. เมื่อได้รับข้อความใหม่จาก Server (Real-time)
    socket.on('receive_message', (data) => {
        // สร้างข้อมูล sender_username ขึ้นมาเองเพื่อให้ฟังก์ชัน displayMessage ทำงานได้
        const displayData = { ...data, sender_username: data.username };
        displayMessage(displayData);
    });
});