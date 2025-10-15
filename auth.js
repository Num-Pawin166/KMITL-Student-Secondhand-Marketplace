// frontend/auth.js

// ฟังก์ชันนี้จะทำงานทันทีเพื่อตรวจสอบการล็อกอิน
(async function checkAuthentication() {
    // ไม่ต้องทำอะไรถ้าเราอยู่ที่หน้า Login อยู่แล้ว
    if (window.location.pathname.endsWith('User-Login.html')) {
        return;
    }

    try {
        const response = await fetch('http://127.0.0.1:5000/api/check-auth', {
            method: 'GET',
            credentials: 'include'
        });

        if (response.status === 401) {
            // ถ้า Backend ตอบว่ายังไม่ login (401 Unauthorized)
            // ให้เปลี่ยนหน้าไปที่ User-Login.html ทันที
            window.location.href = 'User-Login.html';
        }
        // ถ้า status เป็น 200 (OK) ก็ไม่ต้องทำอะไร ปล่อยให้หน้าเว็บโหลดต่อไป
    } catch (error) {
        console.error('Authentication check failed:', error);
        // ถ้าเกิด error (เช่น backend ปิด) ก็ให้ไปหน้า login ก่อนเพื่อความปลอดภัย
        window.location.href = 'User-Login.html';
    }
})();