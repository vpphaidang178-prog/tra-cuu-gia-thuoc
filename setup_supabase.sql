-- ============================================================
-- Supabase Setup Script
-- Tạo tất cả bảng cần thiết cho ứng dụng Tra Cứu Giá Thuốc
-- Chạy script này trong Supabase Dashboard > SQL Editor
-- ============================================================

-- 1. Bảng user_profiles (nếu chưa có)
CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    username TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'user')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
    ON public.user_profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Service role full access to profiles"
    ON public.user_profiles FOR ALL
    USING (true)
    WITH CHECK (true);

-- 2. Thuốc Generic (Mua sắm công)
CREATE TABLE IF NOT EXISTS public.thuoc_generic (
    id BIGSERIAL PRIMARY KEY,
    stt TEXT, ten_thuoc TEXT, ten_hoat_chat TEXT,
    nong_do_ham_luong TEXT, gdklh TEXT, duong_dung TEXT,
    dang_bao_che TEXT, han_dung TEXT, ten_co_so_san_xuat TEXT,
    nuoc_san_xuat TEXT, quy_cach_dong_goi TEXT, don_vi_tinh TEXT,
    so_luong TEXT, don_gia TEXT, nhom_thuoc TEXT, ma_tbmt TEXT,
    ten_cdt TEXT, hinh_thuc_lcnt TEXT, ngay_dang_tai TEXT,
    so_quyet_dinh TEXT, ngay_ban_hanh TEXT, so_nha_thau TEXT,
    dia_diem TEXT
);

ALTER TABLE public.thuoc_generic ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read thuoc_generic" ON public.thuoc_generic FOR SELECT USING (true);
CREATE POLICY "Service write thuoc_generic" ON public.thuoc_generic FOR ALL USING (true) WITH CHECK (true);

-- 3. Thuốc Biệt dược gốc
CREATE TABLE IF NOT EXISTS public.thuoc_biet_duoc (
    id BIGSERIAL PRIMARY KEY,
    stt TEXT, ten_thuoc TEXT, ten_hoat_chat TEXT,
    nong_do_ham_luong TEXT, gdklh TEXT, duong_dung TEXT,
    dang_bao_che TEXT, han_dung TEXT, ten_co_so_san_xuat TEXT,
    nuoc_san_xuat TEXT, quy_cach_dong_goi TEXT, don_vi_tinh TEXT,
    so_luong TEXT, don_gia TEXT, nhom_thuoc TEXT, ma_tbmt TEXT,
    ten_cdt TEXT, hinh_thuc_lcnt TEXT, ngay_dang_tai TEXT,
    so_quyet_dinh TEXT, ngay_ban_hanh TEXT, so_nha_thau TEXT,
    dia_diem TEXT
);

ALTER TABLE public.thuoc_biet_duoc ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read thuoc_biet_duoc" ON public.thuoc_biet_duoc FOR SELECT USING (true);
CREATE POLICY "Service write thuoc_biet_duoc" ON public.thuoc_biet_duoc FOR ALL USING (true) WITH CHECK (true);

-- 4. Thuốc Dược liệu
CREATE TABLE IF NOT EXISTS public.thuoc_duoc_lieu (
    id BIGSERIAL PRIMARY KEY,
    stt TEXT, ten_thuoc TEXT, ten_hoat_chat TEXT,
    nong_do_ham_luong TEXT, gdklh TEXT, duong_dung TEXT,
    dang_bao_che TEXT, han_dung TEXT, ten_co_so_san_xuat TEXT,
    nuoc_san_xuat TEXT, quy_cach_dong_goi TEXT, don_vi_tinh TEXT,
    so_luong TEXT, don_gia TEXT, nhom_thuoc TEXT, ma_tbmt TEXT,
    ten_cdt TEXT, hinh_thuc_lcnt TEXT, ngay_dang_tai TEXT,
    so_quyet_dinh TEXT, ngay_ban_hanh TEXT, so_nha_thau TEXT,
    dia_diem TEXT
);

ALTER TABLE public.thuoc_duoc_lieu ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read thuoc_duoc_lieu" ON public.thuoc_duoc_lieu FOR SELECT USING (true);
CREATE POLICY "Service write thuoc_duoc_lieu" ON public.thuoc_duoc_lieu FOR ALL USING (true) WITH CHECK (true);

-- 5. Dược liệu (nguyên liệu thô)
CREATE TABLE IF NOT EXISTS public.duoc_lieu (
    id BIGSERIAL PRIMARY KEY,
    stt TEXT, ten_duoc_lieu TEXT, bo_phan_dung TEXT,
    ten_khoa_hoc TEXT, nguon_goc TEXT, phuong_phap_che_bien TEXT,
    so_dklh_giay_phep TEXT, ten_co_so_san_xuat TEXT,
    nuoc_san_xuat TEXT, quy_cach_dong_goi TEXT, don_vi_tinh TEXT,
    so_luong TEXT, don_gia_trung_thau TEXT, nhom_tckt TEXT,
    ma_tbmt TEXT, ten_cdt TEXT, hinh_thuc_lcnt TEXT,
    ngay_dang_tai TEXT, so_quyet_dinh TEXT, ngay_ban_hanh TEXT,
    so_nha_thau TEXT, dia_diem TEXT
);

ALTER TABLE public.duoc_lieu ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read duoc_lieu" ON public.duoc_lieu FOR SELECT USING (true);
CREATE POLICY "Service write duoc_lieu" ON public.duoc_lieu FOR ALL USING (true) WITH CHECK (true);

-- 6. Vị thuốc cổ truyền
CREATE TABLE IF NOT EXISTS public.vi_thuoc (
    id BIGSERIAL PRIMARY KEY,
    stt TEXT, ten_vi_thuoc TEXT, bo_phan_dung TEXT,
    ten_khoa_hoc TEXT, nguon_goc TEXT, phuong_phap_che_bien TEXT,
    so_dklh_giay_phep TEXT, ten_co_so_san_xuat TEXT,
    nuoc_san_xuat TEXT, quy_cach_dong_goi TEXT, don_vi_tinh TEXT,
    so_luong TEXT, don_gia_trung_thau TEXT, nhom_tckt TEXT,
    ma_tbmt TEXT, ten_cdt TEXT, hinh_thuc_lcnt TEXT,
    ngay_dang_tai TEXT, so_quyet_dinh TEXT, ngay_ban_hanh TEXT,
    so_nha_thau TEXT, dia_diem TEXT
);

ALTER TABLE public.vi_thuoc ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read vi_thuoc" ON public.vi_thuoc FOR SELECT USING (true);
CREATE POLICY "Service write vi_thuoc" ON public.vi_thuoc FOR ALL USING (true) WITH CHECK (true);

-- 7. Bảo hiểm xã hội (BHXH)
CREATE TABLE IF NOT EXISTS public.bhxh (
    id BIGSERIAL PRIMARY KEY,
    ma_tinh TEXT, ten_tinh TEXT, ten_don_vi TEXT,
    ma_co_so_kcb TEXT, ten_thuoc TEXT, hoat_chat TEXT,
    duong_dung TEXT, dang_bao_che TEXT, ham_luong TEXT,
    dong_goi TEXT, so_dang_ky TEXT, nha_san_xuat TEXT,
    nuoc_san_xuat TEXT, don_vi_tinh TEXT, so_luong TEXT,
    gia TEXT, thanh_tien TEXT, ten_nha_thau TEXT,
    quyet_dinh TEXT, ngay_cong_bo TEXT, nhom_tckt TEXT,
    loai_thuoc TEXT
);

ALTER TABLE public.bhxh ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read bhxh" ON public.bhxh FOR SELECT USING (true);
CREATE POLICY "Service write bhxh" ON public.bhxh FOR ALL USING (true) WITH CHECK (true);

-- ============================================================
-- HOÀN TẤT! Tất cả 7 bảng đã được tạo.
-- ============================================================
