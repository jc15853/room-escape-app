import io
import os
import re
import requests
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# -----------------------------------------------------------------------------
# 0. 페이지 설정 및 세션 상태 초기화
# -----------------------------------------------------------------------------
st.set_page_config(page_title="HELP ME... ☠️", page_icon="🩸", layout="centered")

if 'stage' not in st.session_state:
    st.session_state.stage = 'intro'
if 'hp' not in st.session_state:
    st.session_state.hp = 3
if 'inventory' not in st.session_state:
    st.session_state.inventory = []
if 'player_name' not in st.session_state:
    st.session_state.player_name = ""
if 'sound_to_play' not in st.session_state:
    st.session_state.sound_to_play = None

# -----------------------------------------------------------------------------
# 1. 극강 호러 CSS (상단 흰색 막대 제거 + 글리치 + 핏빛 깜빡임)
# -----------------------------------------------------------------------------
horror_css = """
<style>
    /* 1. 상단 흰색 막대 및 헤더 완전 제거 */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    footer {
        display: none !important;
    }
    .stApp > header {
        background-color: transparent !important;
    }
    div[data-testid="stDecoration"] {
        display: none !important;
    }

    /* 2. 어두운 검은색 배경 & 화면 붉은빛 깜빡임 애니메이션 */
    @keyframes flicker {
        0% { background-color: #050000; }
        50% { background-color: #0d0000; }
        52% { background-color: #1a0000; }
        54% { background-color: #050000; }
        100% { background-color: #050000; }
    }
    .stApp {
        background-color: #050000;
        animation: flicker 4s infinite;
        color: #e6e6e6;
        font-family: 'Courier New', monospace;
    }

    /* 3. 기괴한 타이틀 스타일링 & 글로우 효과 */
    h1, h2, h3 {
        color: #ff0000 !important;
        text-shadow: 0 0 10px #ff0000, 0 0 20px #8b0000, 0 0 30px #000;
        letter-spacing: 2px;
    }

    /* 4. 섬뜩한 경고 알림 박스 */
    .stAlert {
        background-color: #120000 !important;
        border: 2px solid #ff0000 !important;
        color: #ff4d4d !important;
        box-shadow: 0 0 15px rgba(255, 0, 0, 0.5);
    }

    /* 5. 선택창 라디오 버튼 호러 디자인 */
    div[role="radiogroup"] > label {
        background-color: #0a0a0a;
        padding: 12px 18px;
        border-radius: 4px;
        border: 1px solid #440000;
        margin-bottom: 8px;
        color: #ffaaaa !important;
    }
    div[role="radiogroup"] > label:hover {
        border-color: #ff0000;
        background-color: #1a0000;
        box-shadow: 0 0 10px #ff0000;
    }

    /* 6. 피 칠갑 느낌의 버튼 */
    .stButton > button {
        background: linear-gradient(180deg, #330000 0%, #110000 100%) !important;
        color: #ff3333 !important;
        border: 1px solid #ff0000 !important;
        font-size: 1.1rem !important;
        font-weight: bold;
        letter-spacing: 1px;
    }
    .stButton > button:hover {
        background: #ff0000 !important;
        color: #000000 !important;
        box-shadow: 0 0 20px #ff0000;
        transform: scale(1.02);
    }
</style>
"""
st.markdown(horror_css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 강렬한 호러 오디오 플레이어
# -----------------------------------------------------------------------------
SOUND_EFFECTS = {
    'error': 'https://assets.mixkit.co/active_storage/sfx/2688/2688-preview.mp3',   # 섬뜩한 비명/귀신 소리
    'success': 'https://assets.mixkit.co/active_storage/sfx/2568/2568-preview.mp3'  # 웅장하고 어두운 철컥음
}

def play_sound(sound_key):
    sound_url = SOUND_EFFECTS.get(sound_key)
    if sound_url:
        sound_html = f"""
            <iframe src="{sound_url}" allow="autoplay" style="display:none" id="iframeAudio"></iframe>
            <audio autoplay style="display:none">
                <source src="{sound_url}" type="audio/mpeg">
            </audio>
        """
        st.components.v1.html(sound_html, height=0)

# -----------------------------------------------------------------------------
# 3. 폰트 및 잔혹한 탈출 증명서 생성
# -----------------------------------------------------------------------------
@st.cache_resource
def get_korean_font(size):
    font_filename = "NanumGothic.ttf"
    font_url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
    if not os.path.exists(font_filename):
        try:
            res = requests.get(font_url, timeout=5)
            with open(font_filename, "wb") as f:
                f.write(res.content)
        except Exception:
            pass
    try:
        return ImageFont.truetype(font_filename, size)
    except Exception:
        return ImageFont.load_default()

def remove_emojis(text):
    emoji_pattern = re.compile(
        "["
        "\U00010000-\U0010FFFF"
        "\u2600-\u27BF"
        "\u2300-\u23FF"
        "\u2B00-\u2BFF"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text).strip()

def generate_cert_image(player_name, remaining_hp):
    width, height = 650, 500
    img = Image.new('RGB', (width, height), color='#050000')
    draw = ImageDraw.Draw(img)

    font_title = get_korean_font(22)
    font_sub = get_korean_font(13)
    font_body = get_korean_font(15)
    font_bold = get_korean_font(17)

    clean_name = remove_emojis(player_name) if player_name else "이름 없는 희생자"

    draw.rectangle([(15, 15), (width-15, height-15)], outline='#ff0000', width=3)
    draw.rectangle([(30, 30), (width-30, 95)], fill='#200000')
    draw.text((width//2, 52), "[ 핏빛 가상 서버: 잔혹 탈출 증명 ]", fill='#ff0000', font=font_title, anchor="mm")
    draw.text((width//2, 80), "SYSTEM: DATA EXFILTRATION PREVENTED", fill='#888888', font=font_sub, anchor="mm")

    draw.text((50, 140), f"생존 희생자: {clean_name}", fill='#ffffff', font=font_bold)
    draw.text((50, 180), f"남아있는 잔여 이성(HP): {'🩸' * remaining_hp} ({remaining_hp}/3)", fill='#ff3333', font=font_body)
    
    msg_lines = [
        "이 자는 피씽과 피비린내 나는 악성코드 바이러스의",
        "환청 속에서 살아남아 어두운 서버실의 쇠사슬을 풀었습니다.",
        "하지만 해커의 시선은 영원히 당신의 뒤를 쫓을 것입니다..."
    ]
    
    y_pos = 240
    for line in msg_lines:
        draw.text((50, y_pos), line, fill='#cccccc', font=font_body)
        y_pos += 30

    draw.rectangle([(width-210, height-100), (width-40, height-40)], outline='#ff0000', fill='#3a0000')
    draw.text((width-125, height-70), "[ 생존 확인 ]", fill='#ff0000', font=font_bold, anchor="mm")

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

# -----------------------------------------------------------------------------
# 4. 상단 상태바 (의식 수준 표시)
# -----------------------------------------------------------------------------
if st.session_state.stage not in ['intro', 'game_over', 'clear']:
    col_status1, col_status2 = st.columns([2, 1])
    with col_status1:
        st.caption(f"👁️ 감시 대상: **{st.session_state.player_name}** | 🎒 습득한 소지품: {', '.join(st.session_state.inventory) if st.session_state.inventory else '없음'}")
    with col_status2:
        st.markdown(f"🩸 잔여 이성(HP): **{'🩸' * st.session_state.hp}** ({st.session_state.hp}/3)")
    st.divider()

if st.session_state.sound_to_play:
    play_sound(st.session_state.sound_to_play)
    st.session_state.sound_to_play = None

# -----------------------------------------------------------------------------
# 5. 호러 게임 스토리 흐름
# -----------------------------------------------------------------------------

# [시작 화면]
if st.session_state.stage == 'intro':
    st.title("☠️ SYSTEM OVERRIDE: 갇혀버린 영혼")
    st.subheader("모니터 너머에서 차가운 숨소리가 느껴진다...")
    st.write("의식을 차려보니 어둡고 차가운 화면 속에 갇혀 있습니다. 누군가 당신의 일거수일투족을 조롱하며 감시하고 있습니다. 잘못된 판단을 내리는 순간, 당신의 모든 개인정보와 영혼은 파기됩니다.")
    st.divider()
    
    name_input = st.text_input("제물(희생자)의 이름을 적어라...", value="김보안")
    
    if st.button("어둠 속으로 발을 내딛는다 🩸", type="primary", use_container_width=True):
        if name_input.strip():
            st.session_state.player_name = name_input.strip()
            st.session_state.stage = 'stage1'
            st.rerun()
        else:
            st.warning("이름을 적지 않으면 어둠이 당신을 잡아먹습니다...")

# [Stage 1]
elif st.session_state.stage == 'stage1':
    st.header("👁️ 1장: 피로 물든 화면의 스미싱")
    st.write("주머니 속 스마트폰이 미친 듯이 진동하며 뜨겁게 달아오릅니다. 화면에는 섬뜩한 붉은 문자가 떠오릅니다.")
    
    st.error("🩸 **[의심스러운 스미싱 SMS]**\n\n'[경고] 당신의 모든 개인정보와 사진이 유출되었습니다. 10분 내로 아래 악성 백신 링크를 누르지 않으면 당신의 가족들에게 치명적인 영상이 전송됩니다: http://bit.ly/hell_virus'")
    
    st.markdown("#### 공포에 질린 당신의 선택은?")
    
    choice = st.radio("선택지를 고르세요:", [
        "1. 두려움에 떨며 홀린 듯 링크를 눌러 다운로드한다.",
        "2. 이것이 사람의 약점을 노린 스미싱 함정임을 간파하고 즉시 메시지를 삭제 및 차단한다.",
        "3. 지인에게 이 링크를 공유해 진짜인지 물어본다."
    ])
    
    if st.button("선택 실행 💀", type="primary"):
        if "2." in choice:
            st.session_state.sound_to_play = 'success'
            st.success("👁️ 함정을 파악했습니다. 스미싱 차단 완료.")
            st.session_state.inventory.append("🗝️ 핏빛 열쇠")
            st.session_state.stage = 'stage2'
            st.rerun()
        else:
            st.session_state.sound_to_play = 'error'
            st.session_state.hp -= 1
            if st.session_state.hp <= 0:
                st.session_state.stage = 'game_over'
            else:
                st.error("💥 [오답!] 링크를 누르자마자 모든 개인정보와 연락처가 해커의 서버로 털려나갔습니다! (이성 -1)")
            st.rerun()

# [Stage 2]
elif st.session_state.stage == 'stage2':
    st.header("⛓️ 2장: 무차별 대입 공격의 단상")
    st.write("앞을 막아서는 굳게 닫힌 철문. 중앙 단말기에는 **'해커의 무차별 대입 공격(Brute Force)을 견뎌낼 강력한 암호를 설정하라'**는 메시지가 붉은 글씨로 번뜩입니다.")
    
    pw_choice = st.selectbox("어떤 비밀번호를 주입하시겠습니까?", [
        "12345678 (1초 만에 뚫리는 숫자)",
        "password123! (흔하게 예측 가능한 단어 조합)",
        "K#9x!mP2$qL1 (대소문자, 숫자, 특수문자가 조합된 12자리 이상 무작위 암호)",
        "mybirth990101 (생년월일이 포함된 비밀번호)"
    ])
    
    if st.button("암호 주입 🔐", type="primary"):
        if "K#9x!mP2$qL1" in pw_choice:
            st.session_state.sound_to_play = 'success'
            st.success("👁️ 강력한 암호화 알고리즘이 해커의 공격을 무력화시켰습니다.")
            st.session_state.inventory.append("💾 방화벽 서킷")
            st.session_state.stage = 'stage3'
            st.rerun()
        else:
            st.session_state.sound_to_play = 'error'
            st.session_state.hp -= 1
            if st.session_state.hp <= 0:
                st.session_state.stage = 'game_over'
            else:
                st.error("💥 [오답!] 단순한 비밀번호가 0.1초 만에 뚫리며 끔찍한 바이러스에 감염되었습니다! (이성 -1)")
            st.rerun()

# [Stage 3]
elif st.session_state.stage == 'stage3':
    st.header("🚪 3장: 마지막 문과 랜섬웨어의 비명")
    st.write("마지막 출구 문 바로 앞. 서버 본체에서 기괴한 기계음과 비명 소리가 울려 퍼집니다. 시스템이 랜섬웨어에 오염되기 직전입니다.")
    
    action = st.radio("서버를 정화하고 탈출할 방법은?", [
        "1. 공식 정품 백신 프로그램을 실시간 업데이트하여 최신 바이러스 패턴을 정밀 검사한다.",
        "2. 길거리 바닥에 떨어져 있던 수상한 USB를 서버 본체에 연결한다.",
        "3. 랜섬웨어 경고 메시지가 떠도 그냥 모니터를 꺼버린다."
    ])
    
    if st.button("최종 정화 실행 🩸", type="primary"):
        if "1." in action:
            st.session_state.sound_to_play = 'success'
            st.session_state.stage = 'clear'
            st.rerun()
        else:
            st.session_state.sound_to_play = 'error'
            st.session_state.hp -= 1
            if st.session_state.hp <= 0:
                st.session_state.stage = 'game_over'
            else:
                st.error("💥 [오답!] 랜섬웨어가 모든 데이터를 암호화하며 시스템이 마비되었습니다! (이성 -1)")
            st.rerun()

# [게임 오버]
elif st.session_state.stage == 'game_over':
    st.session_state.sound_to_play = 'error'
    st.error("☠️ SYSTEM FATAL ERROR: YOU DIED")
    st.title("💀 당신의 영혼은 영원히 백업되지 않습니다.")
    st.write("모든 이성을 잃었습니다. 해커가 당신의 존재를 시스템에서 완전 삭제했습니다.")
    st.divider()
    
    if st.button("🔄 끊어진 의식을 다시 연결한다 (재도전)", type="primary"):
        st.stage = 'intro'
        st.session_state.stage = 'intro'
        st.session_state.hp = 3
        st.session_state.inventory = []
        st.rerun()

# [탈출 성공]
elif st.session_state.stage == 'clear':
    st.title("🩸 차가운 어둠을 뚫고 생존했습니다.")
    st.write(f"희생자 **{st.session_state.player_name}**님은 사이버 보안의 법칙을 완벽히 이해하고 악령 같은 바이러스를 물리쳤습니다.")
    st.divider()
    
    st.subheader("📜 잔혹 탈출 증명서")
    cert_img = generate_cert_image(st.session_state.player_name, st.session_state.hp)
    
    st.download_button(
        label="📸 생존 증명서(PNG) 내려받기",
        data=cert_img,
        file_name=f"{st.session_state.player_name}_생존증명서.png",
        mime="image/png",
        type="primary",
        use_container_width=True
    )
    
    st.divider()
    if st.button("🔄 처음으로 돌아가기"):
        st.session_state.stage = 'intro'
        st.session_state.hp = 3
        st.session_state.inventory = []
        st.rerun()
