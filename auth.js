// frontend/auth.js

// ฟังก์ชันนี้จะทำงานทันที
(async function checkAuthentication() {
    try {
        // ถาม Backend ว่าเรา login หรือยัง
        const response = await fetch('http://127.0.0.1:5000/api/check-auth', {
            method: 'GET',
            // credentials 'include' สำคัญมากเพื่อให้ browser ส่ง session cookie ไปด้วย
            credentials: 'include' 
        });

        if (response.status === 401) {
            // ถ้า Backend ตอบว่ายังไม่ login (401 Unauthorized)
            // ให้เปลี่ยนหน้าไปที่ login.html ทันที
            window.location.href = 'User-Login.html';
        }
        // ถ้า status เป็น 200 (OK) ก็ไม่ต้องทำอะไร ปล่อยให้หน้าเว็บโหลดต่อไป
    } catch (error) {
        console.error('Authentication check failed:', error);
        // ถ้าเกิด error (เช่น backend ปิด) ก็ให้ไปหน้า login ก่อนเพื่อความปลอดภัย
        window.location.href = 'User-Login.html';
    }
})();