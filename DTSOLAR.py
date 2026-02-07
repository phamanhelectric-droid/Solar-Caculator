import streamlit as st
import pandas as pd
import sys
import subprocess

# --- 1. DỮ LIỆU ĐẦU TƯ ---
investment_data = [
    {"kwh": 300, "tien": 810000, "von": 55000000, "kwp_goi": 2.5},
    {"kwh": 400, "tien": 1139600, "von": 65000000, "kwp_goi": 3.5},
    {"kwh": 700, "tien": 1925220, "von": 80000000, "kwp_goi": 5.5},
    {"kwh": 800, "tien": 2754400, "von": 105000000, "kwp_goi": 7.0},
    {"kwh": 1000, "tien": 3627140, "von": 130000000, "kwp_goi": 8.5},
    {"kwh": 1500, "tien": 5808990, "von": 200000000, "kwp_goi": 14.0},
]

# --- 2. HỆ SỐ PVout LÝ THUYẾT 2026 (34 Tỉnh Thành) ---
pv_data = {
    "Tuyên Quang": [49,37,52,68,108,109,120,112,107,93,80,63],
    "Cao Bằng": [57,54,62,77,108,115,115,114,110,98,86,69],
    "Lai Châu": [105,107,128,134,139,104,119,117,118,111,108,101],
    "Lào Cai": [89,92,104,111,120,113,114,108,101,92,91,88],
    "Thái Nguyên": [51,36,51,65,101,102,119,105,104,91,78,60],
    "Điện Biên": [110,112,129,133,139,112,123,118,123,117,111,104],
    "Lạng Sơn": [58,42,55,68,99,103,118,103,103,91,79,63],
    "Sơn La": [106,103,117,121,126,120,125,120,119,114,108,102],
    "Phú Thọ": [46,39,54,69,103,109,109,108,100,88,76,55],
    "Bắc Ninh": [47,35,49,63,98,100,108,102,95,89,75,55],
    "Quảng Ninh": [55,43,57,69,98,102,109,105,100,95,81,63],
    "Hà Nội": [44,33,47,63,100,105,110,104,96,85,73,52],
    "Hải Phòng": [47,33,47,61,97,101,106,102,92,87,74,55],
    "Hưng Yên": [45,31,45,62,99,106,109,103,93,84,72,52],
    "Ninh Bình": [53,34,49,67,109,116,120,104,98,83,74,57],
    "Thanh Hóa": [64,45,61,80,123,129,132,115,107,90,82,66],
    "Nghệ An": [104,85,100,108,116,121,112,112,114,99,99,99],
    "Hà Tĩnh": [80,62,84,118,121,133,123,120,101,77,69,64],
    "Quảng Trị": [87,74,92,113,125,133,114,125,103,84,84,82],
    "Huế": [93,83,99,116,131,135,119,135,106,89,88,84],
    "Đà Nẵng": [97,86,113,131,144,139,125,139,120,95,95,86],
    "Quảng Ngãi": [119,121,138,145,145,136,125,129,115,108,107,108],
    "Gia Lai": [120,116,138,150,143,133,119,141,119,113,106,98],
    "Đắk Lắk": [109,114,145,148,149,142,133,139,126,113,99,92],
    "Khánh Hòa": [111,115,146,152,155,152,145,153,135,117,100,94],
    "Lâm Đồng": [139,139,161,152,142,129,118,130,115,121,117,120],
    "Đồng Nai": [140,139,150,146,141,127,122,120,113,121,122,129],
    "Tây Ninh": [113,106,123,122,130,124,115,125,105,114,110,110],
    "Hồ Chí Minh": [119,110,132,126,133,120,115,123,106,116,112,114],
    "Đồng Tháp": [118,111,126,127,124,112,110,118,99,106,104,107],
    "An Giang": [123,113,121,123,123,108,104,111,96,106,105,112],
    "Vĩnh Long": [112,111,128,124,121,109,104,112,97,100,100,103],
    "Cần Thơ": [111,108,121,121,118,103,99,106,94,97,97,102],
    "Cà Mau": [109,104,117,120,119,99,96,100,90,97,95,101]
}

def main():
    st.set_page_config(page_title="DTSOLAR - Tư vấn Đầu tư", layout="wide")
    st.title("☀️ PHẦN MỀM TƯ VẤN ĐẦU TƯ ĐIỆN MẶT TRỜI")

    with st.sidebar:
        st.header("📍 Cài đặt")
        # Mặc định chọn Cà Mau
        list_tinh = sorted(list(pv_data.keys()))
        tinh_chon = st.selectbox("Chọn Tỉnh/Thành phố:", list_tinh, index=list_tinh.index("Cà Mau"))
        tien_dien = st.number_input("Tiền điện hàng tháng (VNĐ):", min_value=0, value=2000000, step=100000)
        gio_nang = st.number_input("Số giờ nắng trung bình/ngày (h):", min_value=1.0, value=4.0, step=0.1)

    # --- LOGIC TÍNH TOÁN ---
    # Tra cứu gói đầu tư
    goi_chon = investment_data[0]
    for item in investment_data:
        if (tien_dien <= item["tien"]):
            goi_chon = item
            break
        goi_chon = item

    # Tính kWp cần thiết (4h nắng)
    kwh_ngay = goi_chon["kwh"] / 30
    kwp_can_thiet = kwh_ngay / gio_nang

    # Sản lượng hàng tháng
    he_so_tinh = pv_data[tinh_chon]
    san_luong_thang = [round(h * goi_chon["kwp_goi"], 1) for h in he_so_tinh]
    sl_tb_thang = sum(san_luong_thang) / 12
    hoan_von = goi_chon["von"] / (tien_dien * 12)

    # --- HIỂN THỊ ---
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Vốn đầu tư", f"{goi_chon['von']:,} đ")
    c2.metric("Cần lắp", f"{round(kwp_can_thiet, 2)} kWp")
    c3.metric("Sản lượng TB", f"{round(sl_tb_thang, 1)} kWh")
    c4.metric("Hoàn vốn", f"{round(hoan_von, 1)} năm")

    # BIỂU ĐỒ - Sắp xếp Tháng 01 -> 12
    st.subheader(f"📊 Dự báo sản lượng tại {tinh_chon} ")
    chart_data = pd.DataFrame({
        "Tháng": [f"Tháng {str(i+1).zfill(2)}" for i in range(12)],
        "Sản lượng (kWh)": san_luong_thang
    })
    st.bar_chart(chart_data, x="Tháng", y="Sản lượng (kWh)", color="#fbc02d")

    # --- LIÊN HỆ ---
    st.divider()
    st.subheader("📞 THÔNG TIN TƯ VẤN & LẮP ĐẶT")
    c_info1, c_info2 = st.columns(2)
    with c_info1:
        st.write(f"**Kỹ sư tư vấn:** Phạm Văn Khê")
        st.write(f"**Kinh nghiệm:** 16 năm trong ngành")
        st.write(f"**Vùng hỗ trợ:** Cà Mau & Miền Tây")
    with c_info2:
        st.write("**Điện thoại:** 0909008231")
        st.write("**Zalo:** [0909008231]")
        st.caption("Nguồn dữ liệu: Viện Khí Hậu ")

if __name__ == '__main__':
    if st.runtime.exists():
        main()
    else:
        subprocess.run([sys.executable, "-m", "streamlit", "run", __file__])
