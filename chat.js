// frontend/chat.js
document.addEventListener('DOMContentLoaded', async () => {
    // 1. เชื่อมต่อกับ Socket.IO server ที่ Backend
    const socket = io.connect();
    
    // 2. ดึงข้อมูลจำเป็นจาก URL และ HTML
    const urlParams = new URLSearchParams(window.location.search);
    const productId = urlParams.get('product_id');
    const sellerId = urlParams.get('seller_id');
    const roomName = `product_${productId}`; // สร้างชื่อห้องแชทที่ไม่ซ้ำกันสำหรับสินค้าแต่ละชิ้น

    const chatMessagesContainer = document.querySelector('.chat-messages');
    const chatForm = document.querySelector('.chat-input-form');
    const messageInput = chatForm.querySelector('input');
    
    let currentUser = null;

    // 3. ดึงข้อมูลผู้ใช้ที่ล็อกอินอยู่ เพื่อจะได้รู้ว่าใครเป็นคนส่งข้อความ
    try {
        const response = await fetch('/api/check-auth', { credentials: 'include' });
        if (response.ok) {
            const data = await response.json();
            currentUser = data.user;
        } else {
            throw new Error('User not authenticated');
        }
    } catch (error) {
        console.error('Authentication failed:', error);
        alert('กรุณาล็อกอินเพื่อใช้งานระบบแชท');
        window.location.href = 'User-Login.html';
        return;
    }

    // 4. เมื่อเชื่อมต่อกับ Server สำเร็จ ให้ส่งข้อมูลเพื่อ "เข้าร่วมห้องแชท"
    socket.on('connect', () => {
        console.log('Connected to chat server!');
        socket.emit('join', { username: currentUser.username, room: roomName });
    });

    // 5. เมื่อมีการกดส่งข้อความในฟอร์ม
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const message = messageInput.value;
        if (message.trim()) {
            // ส่งข้อมูลข้อความไปให้ Server
            socket.emit('send_message', {
                username: currentUser.username,
                message: message,
                room: roomName
            });
            messageInput.value = ''; // เคลียร์ช่อง input
        }
    });

    // 6. เมื่อได้รับข้อความใหม่จาก Server
    socket.on('receive_message', (data) => {
        // สร้าง HTML element สำหรับข้อความใหม่
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        
        // ตรวจสอบว่าเป็นข้อความที่ "เราส่งเอง" หรือ "เราได้รับ" เพื่อจัดสไตล์ให้ถูกฝั่ง
        if (data.username === currentUser.username) {
            messageDiv.classList.add('sent');
        } else {
            messageDiv.classList.add('received');
        }
        
        const timestamp = new Date().toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' });

        messageDiv.innerHTML = `
            <p>${data.message}</p>
            <span class="timestamp">${timestamp}</span>
        `;
        
        // นำข้อความใหม่ไปแสดงผล
        chatMessagesContainer.appendChild(messageDiv);
        // เลื่อน scroll ไปที่ข้อความล่าสุด
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    });
});