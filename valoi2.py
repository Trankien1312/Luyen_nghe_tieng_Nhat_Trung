import streamlit as st
import random
from gtts import gTTS
import os
import base64
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

# --- 2. HÀM TẠO SỐ VỚI LOGIC LÀM TRÒN LŨY TIẾN ---
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

# --- 3. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="App Luyện Nghe Pro", layout="wide")

if 'target_value' not in st.session_state:
    st.session_state.update({
        'target_value': "", 'display_answer': False, 'input_key': 0, 
        'check_status': 'idle', 'audio_bytes': None,
        'play_sound': None
    })

SOUND_OK = "https://www.myinstants.com/media/sounds/correct_F677v9p.mp3"
SOUND_FAIL = "https://www.myinstants.com/media/sounds/erro.mp3"

# --- 4. DÀN TRANG 3 CỘT ---
col_left, col_main, col_right = st.columns([1.5, 4, 1.5], gap="large")

with col_left:
    st.write("\n" * 10) 
    if st.session_state.check_status == "correct":
        st.markdown("<h1 style='text-align: center; font-size: 100px;'>🥳</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: green;'>Tuyệt quá!</h3>", unsafe_allow_html=True)
    elif st.session_state.check_status == "wrong":
        st.markdown("<h1 style='text-align: center; font-size: 100px;'>😤</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: red;'>Sai rồi!</h3>", unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='text-align: center; font-size: 100px;'>🤔</h1>", unsafe_allow_html=True)

with col_right:
    st.write("\n" * 10)
    if st.session_state.check_status == "correct":
        st.markdown("<h1 style='text-align: center; font-size: 100px;'>✨</h1>", unsafe_allow_html=True)
    elif st.session_state.check_status == "wrong":
        st.markdown("<h1 style='text-align: center; font-size: 100px;'>💢</h1>", unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='text-align: center; font-size: 100px;'>🎧</h1>", unsafe_allow_html=True)

with col_main:
    st.title("🎧 App Luyện Phản Xạ Pro")
    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a: lang = st.selectbox("🌐 Ngôn ngữ", ["Tiếng Nhật (ja)", "Tiếng Trung (zh-CN)"])
    with col_b: mode = st.selectbox("📊 Loại hình", ["Số đếm", "Ngày tháng", "Phần trăm (%)", "Khoảng thời gian (n trước/sau)", "Thời gian tổng hợp"])

    limit_option = 100000
    difficulty = "Dễ"
    if mode in ["Số đếm", "Phần trăm (%)"]:
        c3, c4 = st.columns(2)
        with c3: difficulty = st.selectbox("⭐ Cấp độ", ["Dễ", "Trung bình", "Khó"])
        with c4: limit_option = st.select_slider("🚀 Giới hạn", options=[100, 1000, 10000, 100000, 1000000, 100000000, 1000000000, 9999999999999], value=100000, format_func=lambda x: f"{x:,}")

    if st.button("🔔 PHÁT NỘI DUNG MỚI", use_container_width=True):
        lang_key = "ja" if "Nhật" in lang else "zh-CN"
        
        if mode == "Số đếm": 
            st.session_state.target_value = str(generate_number_by_difficulty(limit_option, difficulty))
        elif mode == "Ngày tháng": 
            st.session_state.target_value = f"{random.randint(1990, 2026)}年{random.randint(1, 12)}月{random.randint(1, 28)}日"
        elif mode == "Phần trăm (%)": 
            val = round(random.uniform(0, 100), 1) if random.random() < 0.7 else random.randint(0, 100)
            st.session_state.target_value = f"{val}%"
        elif mode == "Khoảng thời gian (n trước/sau)":
            n = random.randint(1, 10)
            items_ja = [f"{n}日前", f"{n}日後", f"{n}週間前", f"{n}週間後", f"{n}ヶ月前", f"{n}ヶ月後", f"{n}年前", f"{n}年後", "一昨年", "去年", "今年", "来年", "再来年"]
            items_zh = [f"{n}天前", f"{n}天后", f"{n}个星期前", f"{n}个星期后", f"{n}个月前", f"{n}个月后", f"{n}年前", f"{n}年后", "前年", "去年", "今年", "明年", "后年"]
            st.session_state.target_value = random.choice(items_ja if lang_key=="ja" else items_zh)
        elif mode == "Thời gian tổng hợp":
            if lang_key == "ja":
                days = ["", "月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日", "昨日", "今日", "明日"]
                weeks = ["", "先週", "今週", "来週"]
                periods = ["朝", "昼", "夜", "午前", "午後"]
                hours = [f"{i}時" for i in range(1, 13)]
                m = random.randint(0, 59)
                m_str = "" if m == 0 else (f"半" if m == 30 and random.random() < 0.5 else f"{m}分")
                st.session_state.target_value = f"{random.choice(weeks)}{random.choice(days)}{random.choice(periods)}{random.choice(hours)}{m_str}"
            else:
                days = ["", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日", "昨天", "今天", "明天"]
                weeks = ["", "上个星期", "这个星期", "下个星期"]
                periods = ["早上", "中午", "下午", "晚上"]
                hours = [f"{i}点" if i!=2 else "两点" for i in range(1, 13)]
                m = random.randint(0, 59)
                m_str = "" if m == 0 else (f"半" if m == 30 and random.random() < 0.5 else f"{m}分")
                st.session_state.target_value = f"{random.choice(weeks)}{random.choice(days)}{random.choice(periods)}{random.choice(hours)}{m_str}"
            
        st.session_state.update({'display_answer': False, 'check_status': 'idle', 'input_key': st.session_state.input_key + 1, 'play_sound': None})
        
        # Logic phát âm
        raw_val = st.session_state.target_value
        text_to_read = raw_val
        if mode == "Số đếm" or mode == "Phần trăm (%)":
            clean_num = raw_val.replace("%", "")
            if "." in clean_num:
                p1, p2 = clean_num.split(".")
                text_to_read = f"{get_phonetic_reading(int(p1), lang_key if 'ja' in lang else 'zh')}点{p2}"
            else:
                text_to_read = get_phonetic_reading(int(clean_num), lang_key if 'ja' in lang else 'zh')
            if "%" in raw_val:
                text_to_read = f"百分之{text_to_read}" if "zh" in lang_key else f"{text_to_read}パーセント"

        try:
            tts = gTTS(text=text_to_read, lang=lang_key)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            st.session_state.audio_bytes = fp.getvalue()
        except: st.error("Lỗi âm thanh.")

    # --- TRÌNH PHÁT NHẠC (KHÔNG AUTOPLAY ĐỂ TRÁNH LỖI ĐIỆN THOẠI) ---
    if st.session_state.audio_bytes:
        st.audio(st.session_state.audio_bytes, format="audio/mp3")

    st.markdown("### ✍️ Nhập đáp án:")
    user_input = st.text_input("Input", key=f"input_{st.session_state.input_key}", label_visibility="collapsed")

    if st.button("👁️ KIỂM TRA ĐÁP ÁN", use_container_width=True):
        st.session_state.display_answer = True
        u_clean = user_input.replace(",", "").replace(".", "").replace(" ", "").replace("%", "")
        t_clean = st.session_state.target_value.replace("%", "").replace(" ", "").replace(".", "")
        if u_clean == t_clean and user_input != "":
            st.session_state.update({'check_status': 'correct', 'play_sound': 'ok'})
        else:
            st.session_state.update({'check_status': 'wrong', 'play_sound': 'fail'})
        st.rerun()

    if st.session_state.display_answer:
        st.success(f"✅ Đáp án đúng: **{st.session_state.target_value}**")
        if st.session_state.check_status == "correct": st.balloons()

# --- 6. PHÁT ÂM THANH HIỆU ỨNG (ẨN) ---
if st.session_state.play_sound == "ok":
    st.markdown(f'<audio autoplay src="{SOUND_OK}"></audio>', unsafe_allow_html=True)
    st.session_state.play_sound = None 
elif st.session_state.play_sound == "fail":
    st.markdown(f'<audio autoplay src="{SOUND_FAIL}"></audio>', unsafe_allow_html=True)
    st.session_state.play_sound = None
