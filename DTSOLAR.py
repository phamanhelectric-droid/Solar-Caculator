import streamlit as st
import pandas as pd
import sys
import subprocess

# --- 1. DỮ LIỆU ĐẦU TƯ GỐC ---
investment_data = [
    {"kwh": 300, "tien": 810000, "von": 55000000, "kwp_goi": 2.5},
    {"kwh": 400, "tien": 1139600, "von": 65000000, "kwp_goi": 3.5},
    {"kwh": 700, "tien": 1925220, "von": 80000000, "kwp_goi": 5.5},
    {"kwh": 800, "tien": 2754400, "von": 105000000, "kwp_goi": 7.0},
    {"kwh": 1000, "tien": 3627140, "von": 130000000, "kwp_goi": 8.5},
    {"kwh": 1500, "tien": 5808990, "von": 200000000, "kwp_goi": 14.0},
]

# --- 2. DỮ LIỆU BỨC XẠ 34 TỈNH THÀNH 2026 ---
pv_data = {
    # ... (Giữ nguyên danh sách 34 tỉnh thành từ Tuyên Quang đến Cà Mau)
    "Cà Mau": [109, 104, 117, 120, 119, 99, 96, 100, 90, 97, 95, 101],
    "Cần Thơ": [111, 108, 121, 121, 118, 103, 99, 106, 94, 97, 97, 102],
    "Hồ Chí Minh": [119, 110, 132, 126, 133, 120, 115, 123, 106, 116, 112, 114]
}


def main():
    st.set_page_config(page_title="DTSOLAR - Kỹ sư Khê", layout="wide")
    st.title("☀️ TƯ VẤN ĐIỆN MẶT TRỜI TỐI ƯU CHI PHÍ")

    with st.sidebar:
        st.header("📍 Cấu hình")
        list_tinh = sorted(list(pv_data.keys()))
        tinh_chon = st.selectbox("Chọn Tỉnh/Thành phố:", list_tinh, index=list_tinh.index("Cà Mau"))
        tien_dien = st.number_input("Tiền điện hàng tháng (VNĐ):", min_value=0, value=2000000, step=100000)
        gio_nang = st.number_input("Số giờ nắng trung bình/ngày (h):", min_value=1.0, value=4.0, step=0.1)

    # --- LOGIC TÍNH TOÁN CẢI TIẾN ---
    max_goi = investment_data[-1]

    if tien_dien <= max_goi["tien"]:
        # Tra cứu gói từ bảng gốc
        for item in investment_data:
            if (tien_dien <= item["tien"]):
                goi_hien_tai = item
                break
    else:
        # LOGIC ƯU ĐÃI CHO HỆ LỚN:
        # Tính toán kWh dựa trên giá điện trung bình bậc cao (~3.150đ)
        kwh_uoc_tinh = tien_dien / 3150
        kwp_uoc_tinh = (kwh_uoc_tinh / 30) / gio_nang

        # Đơn giá giảm dần: Hệ càng lớn, đơn giá càng thấp (xuống mức ~12.5tr - 13tr/kWp)
        # Giả định đơn giá cho hệ cực lớn là 13.000.000 đ/kWp
        don_gia_khuyen_nghi = 13000000
        von_uoc_tinh = kwp_uoc_tinh * don_gia_khuyen_nghi

        goi_hien_tai = {
            "kwh": kwh_uoc_tinh,
            "tien": tien_dien,
            "von": von_uoc_tinh,
            "kwp_goi": kwp_uoc_tinh
        }

    # Sản lượng hàng tháng
    he_so_tinh = pv_data[tinh_chon]
    san_luong_thang = [round(h * goi_hien_tai["kwp_goi"], 1) for h in he_so_tinh]
    sl_tb_thang = sum(san_luong_thang) / 12
    hoan_von = goi_hien_tai["von"] / (tien_dien * 12)

    # --- HIỂN THỊ ---
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info("📦 **Mức đầu tư**")
        st.metric("Vốn dự kiến", f"{int(goi_hien_tai['von']):,} đ")
        st.caption(f"Đơn giá: ~{int(goi_hien_tai['von'] / goi_hien_tai['kwp_goi']):,} đ/kWp")

    with col2:
        st.error("⚡ **Công suất Pin**")
        st.metric("Cần lắp", f"{round(goi_hien_tai['kwp_goi'], 2)} kWp")
        st.caption(f"Dựa trên {gio_nang}h nắng")

    with col3:
        st.success("🌍 **Sản lượng**")
        st.metric("Sản lượng TB", f"{round(sl_tb_thang, 1)} kWh")
        st.caption(f"Khu vực: {tinh_chon}")

    with col4:
        st.warning("💰 **Tài chính**")
        st.metric("Hoàn vốn", f"{round(hoan_von, 1)} năm")
        st.caption(f"Tiết kiệm: {(tien_dien * 12):,} đ/năm")

    # BIỂU ĐỒ - Sắp xếp 1-12
    st.subheader(f"📈 Biểu đồ sản lượng {tinh_chon} năm 2026")
    df_chart = pd.DataFrame({
        "Tháng": [f"Tháng {str(i + 1).zfill(2)}" for i in range(12)],
        "Sản lượng (kWh)": san_luong_thang
    })
    st.bar_chart(df_chart, x="Tháng", y="Sản lượng (kWh)", color="#fbc02d")

    # --- LIÊN HỆ ---
    st.divider()
    st.write(f"**Kỹ sư tư vấn:** Phạm Văn Khê - 16 năm kinh nghiệm")
    st.write(f"**Vùng hỗ trợ:** Cà Mau & Miền Tây")
    st.write(f"**Số điện thoại liên hệ:** 0909008231")
    st.write(f"**Zalo:** 0909008231")
    st.caption("Dữ liệu: Báo giá chuẩn và PVout 2026")


if __name__ == '__main__':
    main()

