import streamlit as st
import random
from gtts import gTTS
import io # Thư viện quan trọng để xử lý âm thanh trên RAM

# --- 1. HÀM XỬ LÝ HỆ VẠN/ỨC ---
def format_man_oku(n, lang_type):
    try:
        n_int = int(float(n))
        if n_int == 0: return "0"
        units_jp = ["", "万", "億", "兆"]
        units_cn = ["", "万", "亿", "兆"]
        units = units_jp if lang_type == "ja" else units_cn
        result = ""
        for i in range(len(units)):
            part = (n_int // (10000**i)) % 10000
            if part > 0:
                result = f"{part}{units[i]} " + result
        return result.strip()
    except:
        return ""

# --- 2. HÀM TẠO SỐ THEO CẤP ĐỘ ---
def generate_number_by_difficulty(limit, difficulty):
    val = random.randint(0, limit)
    if difficulty == "Khó": return val
    elif difficulty == "Dễ":
        step = 1000 if val > 10000 else 100
        val = (val // step) * step
    elif difficulty == "Trung bình":
        if val > 10000: val = (val // 5) * 5 
    return val

# --- 3. DỮ LIỆU THỜI GIAN VÀ THỨ ---
DATA_TIME = {
    "ja": {
        "weeks": ["先々週", "先週", "今週", "来週", "再来週"],
        "days": ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"],
        "periods": ["朝", "昼", "夜"],
        "hours": [f"{i}時" for i in range(1, 13)]
    },
    "zh-CN": {
        "weeks": ["上上星期", "上星期", "这星期", "下星期", "下下星期"],
        "days": ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"],
        "periods": ["早上", "下午", "晚上"],
        "hours": [f"{i}点" if i != 2 else "两点" for i in range(1, 13)] 
    }
}

# --- 4. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="App Luyện Nghe Pro", layout="wide")

# --- 5. KHỞI TẠO TRẠNG THÁI ---
if 'target_value' not in st.session_state:
    st.session_state.update({
        'target_value': "", 
        'display_answer': False, 
        'input_key': 0,
        'check_status': "idle",
        'generated_mode': "Số đếm",
        'play_sound': None,
        'audio_bytes': None,       # Lưu trực tiếp dữ liệu âm thanh vào RAM
        'autoplay_audio': False    # Công tắc kiểm soát tự động phát
    })

SOUND_OK = "https://www.myinstants.com/media/sounds/correct_F677v9p.mp3"
SOUND_FAIL = "https://www.myinstants.com/media/sounds/erro.mp3"

# --- 6. GIAO DIỆN CHÍNH ---
col_left, col_main, col_right = st.columns([1.5, 4, 1.5], gap="large")

with col_left:
    st.write("\n" * 10) 
    if st.session_state.check_status == "correct":
        st.markdown("<h1 style='text-align: center; font-size: 130px;'>🥳</h1>", unsafe_allow_html=True)
    elif st.session_state.check_status == "wrong":
        st.markdown("<h1 style='text-align: center; font-size: 130px;'>😤</h1>", unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='text-align: center; font-size: 130px;'>🤔</h1>", unsafe_allow_html=True)

with col_right:
    st.write("\n" * 10)
    if st.session_state.check_status == "correct":
        st.markdown("<h1 style='text-align: center; font-size: 130px;'>✨</h1>", unsafe_allow_html=True)
    elif st.session_state.check_status == "wrong":
        st.markdown("<h1 style='text-align: center; font-size: 130px;'>💢</h1>", unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='text-align: center; font-size: 130px;'>🎧</h1>", unsafe_allow_html=True)

with col_main:
    st.title("🎧 App Luyện Phản Xạ Tổng Hợp")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1: lang = st.selectbox("🌐 Ngôn ngữ", ["Tiếng Nhật (ja)", "Tiếng Trung (zh-CN)"])
    with col2: mode = st.selectbox("📊 Loại hình", ["Số đếm", "Ngày tháng", "Phần trăm (%)", "Thứ & Tuần", "Giờ & Buổi"])

    limit_option, difficulty = 1000000, "Khó"
    if mode in ["Số đếm", "Phần trăm (%)"]:
        c3, c4 = st.columns(2)
        with c3: difficulty = st.selectbox("⭐ Cấp độ", ["Dễ", "Trung bình", "Khó"])
        with c4: limit_option = st.select_slider("🚀 Giới hạn", options=[10, 100, 1000, 10000, 100000, 1000000], value=100)

    # --- NÚT TẠO CÂU HỎI MỚI ---
    if st.button("🔔 PHÁT NỘI DUNG MỚI", use_container_width=True):
        st.session_state.generated_mode = mode 
        lang_key = "ja" if "Nhật" in lang else "zh-CN"
        
        if mode == "Số đếm": 
            st.session_state.target_value = str(generate_number_by_difficulty(limit_option, difficulty))
        elif mode == "Ngày tháng": 
            st.session_state.target_value = f"{random.randint(1990, 2026)}年{random.randint(1, 12)}月{random.randint(1, 28)}日"
        elif mode == "Phần trăm (%)": 
            if random.random() < 0.7: val = round(random.uniform(0, limit_option), 1)
            else: val = random.randint(0, limit_option)
            st.session_state.target_value = f"{val}%"
        elif mode == "Thứ & Tuần":
            data = DATA_TIME[lang_key]
            st.session_state.target_value = f"{random.choice(data['weeks'])}{random.choice(data['days'])}"
        elif mode == "Giờ & Buổi":
            data = DATA_TIME[lang_key]
            period = random.choice(data['periods'])
            hour = random.choice(data['hours'])
            minute = random.randint(0, 59)
            min_str = "" if minute == 0 else (f"半" if minute == 30 and random.random() < 0.5 else f"{minute}分")
            st.session_state.target_value = f"{period}{hour}{min_str}"
            
        st.session_state.display_answer = False
        st.session_state.check_status = "idle" 
        st.session_state.play_sound = None 
        st.session_state.input_key += 1 
        
        # XỬ LÝ ÂM THANH TRỰC TIẾP TRÊN RAM (KHÔNG LỖI)
        text_to_read = st.session_state.target_value
        if "%" in text_to_read:
            text_to_read = f"百分之{text_to_read.replace('%','')}" if lang_key=="zh-CN" else f"{text_to_read.replace('%','')}パーセント"
            
        try:
            tts = gTTS(text=text_to_read, lang=lang_key)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            # Lưu dữ liệu âm thanh vào session state
            st.session_state.audio_bytes = fp.getvalue()
            # Bật công tắc Autoplay cho lần render ngay sau đây
            st.session_state.autoplay_audio = True 
        except Exception as e:
            st.error(f"Lỗi tạo âm thanh: {e}")

    # --- HIỂN THỊ TRÌNH PHÁT NHẠC (Luôn hiện nếu có dữ liệu) ---
    if st.session_state.audio_bytes is not None:
        st.audio(st.session_state.audio_bytes, format="audio/mp3", autoplay=st.session_state.autoplay_audio)
        # Tắt Autoplay ngay lập tức để lúc gõ phím nó không bị phát lại
        st.session_state.autoplay_audio = False 

    st.markdown("### ✍️ Nhập đáp án:")
    if st.session_state.generated_mode == "Ngày tháng": ph_text = "VD: 2024年5月10日"
    elif st.session_state.generated_mode == "Thứ & Tuần": ph_text = "VD: 来週月曜日"
    elif st.session_state.generated_mode == "Giờ & Buổi": ph_text = "VD: 夜8時30分"
    else: ph_text = "Nhập số (VD: 11.2 hoặc 22,5)"

    user_input = st.text_input("Input", key=f"input_{st.session_state.input_key}", placeholder=ph_text, label_visibility="collapsed")

    if user_input and st.session_state.generated_mode not in ["Ngày tháng", "Thứ & Tuần", "Giờ & Buổi"]:
        try:
            display_val = float(user_input.replace(",", "."))
            st.info(f"Giá trị bạn đang gõ: **{display_val}**")
        except: pass

    # --- KIỂM TRA ĐÁP ÁN ---
    if st.button("👁️ KIỂM TRA ĐÁP ÁN", use_container_width=True):
        st.session_state.display_answer = True
        ans = str(st.session_state.target_value)
        
        u_clean = user_input.replace(",", ".").replace(" ", "").replace("%", "")
        t_clean = ans.replace("%", "").replace(" ", "")
        
        try: is_correct = (float(u_clean) == float(t_clean))
        except: is_correct = (u_clean == t_clean and u_clean != "")
        
        if is_correct:
            st.session_state.check_status = "correct"
            st.session_state.play_sound = "ok"
        elif user_input == "": st.session_state.check_status = "idle"
        else:
            st.session_state.check_status = "wrong"
            st.session_state.play_sound = "fail"
            
        st.rerun() 

    if st.session_state.display_answer:
        ans = st.session_state.target_value
        l_type = "ja" if "Nhật" in lang else "zh"
        
        if st.session_state.generated_mode in ["Ngày tháng", "Thứ & Tuần", "Giờ & Buổi"]:
            st.success(f"✅ Đáp án đúng: **{ans}**")
        else:
            val_only = ans.replace("%", "")
            st.success(f"✅ Đáp án đúng: **{ans}**")
            if "." in val_only:
                parts = val_only.split(".")
                st.info(f"💡 Phần nguyên: {format_man_oku(parts[0], l_type)}")
            elif val_only.isdigit():
                st.info(f"💡 Hệ Vạn-Ức: {format_man_oku(val_only, l_type)}")
                    
        if st.session_state.check_status == "correct": st.balloons()

# --- 7. PHÁT ÂM THANH ĐÚNG/SAI ---
if st.session_state.play_sound == "ok":
    st.markdown(f'<audio autoplay src="{SOUND_OK}"></audio>', unsafe_allow_html=True)
    st.session_state.play_sound = None 
elif st.session_state.play_sound == "fail":
    st.markdown(f'<audio autoplay src="{SOUND_FAIL}"></audio>', unsafe_allow_html=True)
    st.session_state.play_sound = None