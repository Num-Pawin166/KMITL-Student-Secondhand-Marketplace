// เลือกองค์ประกอบที่ต้องใช้
const decreaseBtn = document.querySelector(".decrease");
const increaseBtn = document.querySelector(".increase");
const quantityEl = document.querySelector(".quantity");
const priceEl = document.querySelector(".price");
const subtotalEl = document.getElementById("subtotal");
const totalEl = document.getElementById("total");

const shippingCost = 20; // ค่าจัดส่ง

// ดึงราคาต่อชิ้นจาก data attribute
const unitPrice = parseInt(priceEl.dataset.price);

// เริ่มต้นจำนวนสินค้า
let quantity = 1;

// ฟังก์ชันอัปเดตยอดรวม
function updatePrice() {
  const subtotal = unitPrice * quantity;
  const total = subtotal + shippingCost;

  subtotalEl.textContent = subtotal.toLocaleString() + " ฿";
  totalEl.textContent = total.toLocaleString() + " ฿";
}

// เมื่อคลิกปุ่ม +
increaseBtn.addEventListener("click", () => {
  quantity++;
  quantityEl.textContent = quantity;
  updatePrice();
});

// เมื่อคลิกปุ่ม -
decreaseBtn.addEventListener("click", () => {
  if (quantity > 1) {
    quantity--;
    quantityEl.textContent = quantity;
    updatePrice();
  }
});
