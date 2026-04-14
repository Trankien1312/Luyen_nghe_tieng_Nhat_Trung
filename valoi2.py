import streamlit as st
import random
from gtts import gTTS
import os
import io

# --- 1. HÀM ĐỊNH DẠNG ĐỌC SỐ ---
def get_phonetic_reading(n_int, lang_key):
    if lang_key == "ja": return str(n_int)
    if n_int == 0: return "零"
    if n_int < 10000: return str(n_int)
    if n_int >= 100000000:
        yi_part = n_int // 100000000
        yi_text = f"{yi_part // 10000}万{yi_part % 10000}亿" if yi_part >= 10000 else f"{yi_part}亿"
        rem_part = n_int % 100000000
        if rem_part > 0:
            return f"{yi_text}{rem_part // 10000}万{rem_part % 10000 if rem_part % 10000 > 0 else ''}".replace("0亿", "亿")
        return yi_text.replace("0亿", "亿")
    return f"{n_int // 10000}万{n_int % 10000 if n_int % 10000 > 0 else ''}"

# --- 2. HÀM TẠO SỐ VỚI LOGIC LÀM TRÒN ---
def generate_number_by_difficulty(limit, difficulty):
    limit = max(int(limit), 1)
    val = random.randint(0, limit)
    if difficulty == "Khó" or val < 10000: return val
    magnitude = len(str(val))
    if difficulty == "Dễ":
        step = 10 ** (magnitude - 2)
        val = (val // step) * step
    elif difficulty == "Trung bình":
        step = 10 ** (magnitude - 3)
        val = (val // step) * step
    return val if val > 0 else random.randint(1, 10)

# --- 3. CẤU HÌNH ---
st.set_page_config(page_title="App Luyện Nghe Master", layout="wide")

if 'target_value' not in st.session_state:
    st.session_state.update({
        'target_value': "", 'display_answer': False, 'input_key': 0, 
        'check_status': 'idle', 'play_sound': None, 'has_audio': False
    })

SOUND_OK = "https://www.myinstants.com/media/sounds/correct_F677v9p.mp3"
SOUND_FAIL = "https://www.myinstants.com/media/sounds/erro.mp3"

# --- 4. GIAO DIỆN 3 CỘT ---
col_left, col_main, col_right = st.columns([1.5, 4, 1.5], gap="large")

with col_left:
    st.write("\n" * 10) 
    if st.session_state.check_status == "correct":
        st.markdown("<h1 style='text-align: center; font-size: 100px;'>🥳</h1>", unsafe_allow_html=True)
    elif st.session_state.check_status == "wrong":
        st.markdown("<h1 style='text-align: center; font-size: 100px;'>😤</h1>", unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='text-align: center; font-size: 100px;'>🤔</h1>", unsafe_allow_html=True)

with col_main:
    st.title("🎧 App Luyện Phản Xạ Pro")
    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a: lang = st.selectbox("🌐 Ngôn ngữ", ["Tiếng Nhật (ja)", "Tiếng Trung (zh-CN)"])
    with col_b: mode = st.selectbox("📊 Loại hình", ["Số đếm", "Ngày tháng", "Phần trăm (%)", "Khoảng thời gian & Thứ", "Thời gian tổng hợp"])

    limit_option = 100000
    difficulty = "Dễ"
    if mode in ["Số đếm", "Phần trăm (%)"]:
        c3, c4 = st.columns(2)
        with c3: difficulty = st.selectbox("⭐ Cấp độ", ["Dễ", "Trung bình", "Khó"])
        with c4: limit_option = st.select_slider("🚀 Giới hạn", options=[100, 1000, 10000, 100000, 1000000, 100000000, 1000000000, 9999999999999], value=100000, format_func=lambda x: f"{x:,}")

    # NÚT PHÁT NỘI DUNG
    if st.button("🔔 PHÁT NỘI DUNG MỚI", use_container_width=True):
        lang_key = "ja" if "Nhật" in lang else "zh-CN"
        
        # Logic tạo nội dung (Tổng hợp từ các yêu cầu trước)
        if mode == "Số đếm": 
            st.session_state.target_value = str(generate_number_by_difficulty(limit_option, difficulty))
        elif mode == "Ngày tháng": 
            st.session_state.target_value = f"{random.randint(1990, 2026)}年{random.randint(1, 12)}月{random.randint(1, 28)}日"
        elif mode == "Phần trăm (%)": 
            st.session_state.target_value = f"{random.randint(0, 100)}%"
        elif mode == "Khoảng thời gian & Thứ":
            n = random.randint(1, 10)
            items_ja = [f"{n}日前", f"{n}日後", "来年", "去年", "月曜日", "金曜日"]
            items_zh = [f"{n}天前", f"{n}天后", "明年", "去年", "星期一", "星期五"]
            st.session_state.target_value = random.choice(items_ja if lang_key=="ja" else items_zh)
        elif mode == "Thời gian tổng hợp":
            st.session_state.target_value = "明日の朝8時" if lang_key=="ja" else "明天早上8点"
            
        st.session_state.update({'display_answer': False, 'check_status': 'idle', 'input_key': st.session_state.input_key + 1, 'play_sound': None})
        
        # Tạo âm thanh và lưu file
        text_to_read = st.session_state.target_value
        if mode == "Số đếm": text_to_read = get_phonetic_reading(int(text_to_read), lang_key)
        
        try:
            tts = gTTS(text=text_to_read, lang=lang_key)
            tts.save("temp_audio.mp3")
            st.session_state.has_audio = True # Đánh dấu đã có audio thành công
        except:
            st.error("Lỗi tạo âm thanh")
            st.session_state.has_audio = False

    # --- KHU VỰC HIỂN THỊ AUDIO (CHỈ HIỆN KHI CÓ DỮ LIỆU) ---
    if st.session_state.has_audio and os.path.exists("temp_audio.mp3"):
        with open("temp_audio.mp3", "rb") as f:
            st.audio(f.read(), format="audio/mp3")
    else:
        st.info("Nhấn nút '🔔 PHÁT NỘI DUNG MỚI' để bắt đầu nghe.")

    st.markdown("### ✍️ Nhập đáp án:")
    user_input = st.text_input("Input", key=f"input_{st.session_state.input_key}", label_visibility="collapsed")

    if st.button("👁️ KIỂM TRA ĐÁP ÁN", use_container_width=True):
        st.session_state.display_answer = True
        u_clean = user_input.replace(",", "").replace(".", "").replace(" ", "")
        t_clean = st.session_state.target_value.replace(" ", "").replace(".", "").replace("%", "")
        if u_clean == t_clean and user_input != "":
            st.session_state.update({'check_status': 'correct', 'play_sound': 'ok'})
        else:
            st.session_state.update({'check_status': 'wrong', 'play_sound': 'fail'})
        st.rerun()

    if st.session_state.display_answer:
        st.success(f"✅ Đáp án đúng: **{st.session_state.target_value}**")
        if st.session_state.check_status == "correct": st.balloons()

with col_right:
    st.write("\n" * 10)
    if st.session_state.check_status == "correct":
        st.markdown("<h1 style='text-align: center; font-size: 100px;'>✨</h1>", unsafe_allow_html=True)
    elif st.session_state.check_status == "wrong":
        st.markdown("<h1 style='text-align: center; font-size: 100px;'>💢</h1>", unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='text-align: center; font-size: 100px;'>🎧</h1>", unsafe_allow_html=True)

# Âm thanh hiệu ứng
if st.session_state.play_sound == "ok":
    st.markdown(f'<audio autoplay src="{SOUND_OK}"></audio>', unsafe_allow_html=True)
    st.session_state.play_sound = None 
elif st.session_state.play_sound == "fail":
    st.markdown(f'<audio autoplay src="{SOUND_FAIL}"></audio>', unsafe_allow_html=True)
    st.session_state.play_sound = None
