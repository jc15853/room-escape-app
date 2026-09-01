import io
import os
import re
import requests
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# -----------------------------------------------------------------------------
# 0. 페이지 설정 및 세션 상태 초기화
# -----------------------------------------------------------------------------
st.set_page_config(page_title="보안 해커의 가상 감옥 💀", page_icon="💀", layout="centered")

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
# 1. 상단 흰색 막대 제거 + 선명한 다크 테마 CSS
# -----------------------------------------------------------------------------
custom_css = """
<style>
    /* 상단 흰색 막대 및 헤더 완벽 제거 */
    header[data-testid="stHeader"], footer, div[data-testid="stDecoration"] {
        display: none !important;
    }

    /* 전체 배경: 깔끔한 어두운 검은색 / 선명한 하얀 글씨 */
    .stApp {
        background-color: #0d1117;
        color: #ffffff;
    }
    
    /* 타이틀 강조 */
    h1, h2, h3 {
        color: #ff4d4d !important;
        font-family: 'Courier New', monospace;
    }
    
    /* 본문 텍스트 높은 가독성 확보 */
    p, span, label {
        color: #e6edf3 !important;
        font-size: 1.05rem;
    }

    /* 에러 및 선택 박스 */
    .stAlert {
        background-color: #161b22 !important;
        border: 1px solid #ff4d4d !important;
        color: #ff8080 !important;
    }

    /* 라디오 버튼 선택창 */
    div[role="radiogroup"] > label {
        background-color: #161b22;
        padding: 12px 16px;
        border-radius: 6px;
        border: 1px solid #30363d;
        margin-bottom: 8px;
    }
    div[role="radiogroup"] > label:hover {
        border-color: #ff4d4d;
        background-color: #21262d;
    }

    /* 버튼 스타일 */
    .stButton > button {
        background-color: #21262d !important;
        color: #ff4d4d !important;
        border: 1px solid #ff4d4d !important;
        font-weight: bold;
        font-size: 1rem;
    }
    .stButton > button:hover {
        background-color: #ff4d4d !important;
        color: #000000 !important;
    }

    /* 주요 실행 버튼 */
    .stButton > button[kind="primary"] {
        background-color: #8b0000 !important;
        color: #ffffff !important;
        border: 1px solid #ff3333 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #ff3333 !important;
        color: #000000 !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 오디오 플레이어 (에러음 / 성공음)
# -----------------------------------------------------------------------------
SOUND_EFFECTS = {
    'error': 'https://assets.mixkit.co/active_storage/sfx/2572/2572-preview.mp3',   # 에러 피직 소리
    'success': 'https://assets.mixkit.co/active_storage/sfx/1435/1435-preview.mp3'  # 띵동 성공음
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
# 3. 인증서 이미지 생성
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
    img = Image.new('RGB', (width, height), color='#111111')
    draw = ImageDraw.Draw(img)

    font_title = get_korean_font(24)
    font_sub = get_korean_font(14)
    font_body = get_korean_font(16)
    font_bold = get_korean_font(18)

    clean_name = remove_emojis(player_name) if player_name else "익명 보안관"

    draw.rectangle([(15, 15), (width-15, height-15)], outline='#ff4d4d', width=4)
    draw.rectangle([(30, 30), (width-30, 95)], fill='#220000')
    draw.text((width//2, 52), "[디지털 보안 감옥 탈출 성공]", fill='#ff4d4d', font=font_title, anchor="mm")
    draw.text((width//2, 80), "사이버 보안 생존 인증서", fill='#ff9999', font=font_sub, anchor="mm")

    draw.text((50, 140), f"생존자 이름: {clean_name}", fill='#ffffff', font=font_bold)
    draw.text((50, 180), f"남은 정신력(HP): {'❤️' * remaining_hp} ({remaining_hp}/3)", fill='#ffffff', font=font_body)
    
    msg_lines = [
        "위 생존자는 해커의 피싱 문자 공포, 암호화된 트랩,",
        "그리고 악성 바이러스의 공격을 무사히 차단하고",
        "어둠 속 가상 서버 감옥을 완벽히 탈출했음을 인증합니다."
    ]
    
    y_pos = 240
    for line in msg_lines:
        draw.text((50, y_pos), line, fill='#d1d5db', font=font_body)
        y_pos += 30

    draw.rectangle([(width-200, height-100), (width-50, height-40)], outline='#ff4d4d', fill='#330000')
    draw.text((width-125, height-70), "[생존 인증]", fill='#ff4d4d', font=font_bold, anchor="mm")

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

# -----------------------------------------------------------------------------
# 4. 상단 상태바
# -----------------------------------------------------------------------------
if st.session_state.stage not in ['intro', 'game_over', 'clear']:
    col_status1, col_status2 = st.columns([2, 1])
    with col_status1:
        st.caption(f"👁️ 생존자: **{st.session_state.player_name}** | 🎒 소지품: {', '.join(st.session_state.inventory) if st.session_state.inventory else '없음'}")
    with col_status2:
        st.markdown(f"🖤 정신력(HP): **{'❤️' * st.session_state.hp}** ({st.session_state.hp}/3)")
    st.divider()

if st.session_state.sound_to_play:
    play_sound(st.session_state.sound_to_play)
    st.session_state.sound_to_play = None

# -----------------------------------------------------------------------------
# 5. 게임 스토리
# -----------------------------------------------------------------------------

# [시작 화면]
if st.session_state.stage == 'intro':
    st.title("💀 해커의 가상 감옥 탈출기")
    st.subheader("수상한 링크를 누른 후, 차가운 화면 속에 갇혀버렸다...")
    st.write("올바른 사이버 보안 선택을 거쳐야만 무사히 탈출할 수 있습니다. 틀리면 정신력이 깎이고 에러 경고음이 울립니다!")
    st.divider()
    
    name_input = st.text_input("당신의 이름을 입력하세요:", value="김보안")
    
    if st.button("게임 시작하기 🔓", type="primary", use_container_width=True):
        if name_input.strip():
            st.session_state.player_name = name_input.strip()
            st.session_state.stage = 'stage1'
            st.rerun()
        else:
            st.warning("이름을 입력해주세요!")

# [Stage 1]
elif st.session_state.stage == 'stage1':
    st.header("📱 1단계: 의심스러운 문자 메시지")
    st.write("스마트폰에 수상한 알림 문자가 도착했습니다.")
    
    st.error("📱 **[수신 문자 내용]**\n\n'[국외발신] 당신의 개인정보가 유출되었습니다. 즉시 아래 링크를 눌러 백신을 설치하지 않으면 데이터가 파기됩니다: http://bit.ly/dark_virus'")
    
    st.markdown("#### 어떻게 행동하시겠습니까?")
    
    choice = st.radio("선택지를 고르세요:", [
        "1. 겁이 나서 즉시 링크를 클릭해 앱을 설치한다.",
        "2. 출처가 불분명한 스미싱 링크임을 알아채고 메시지를 삭제한다.",
        "3. 친구에게 메시지를 전달해서 클릭해달라고 부탁한다."
    ])
    
    if st.button("선택 제출 🩸", type="primary"):
        if "2." in choice:
            st.session_state.sound_to_play = 'success'
            st.success("🎉 올바른 판단입니다! 스미싱 함정을 피했습니다.")
            st.session_state.inventory.append("🗝️ 붉은 열쇠")
            st.session_state.stage = 'stage2'
            st.rerun()
        else:
            st.session_state.sound_to_play = 'error'
            st.session_state.hp -= 1
            if st.session_state.hp <= 0:
                st.session_state.stage = 'game_over'
            else:
                st.error("💥 [틀렸습니다!] 악성 바이러스가 기기에 침투하여 시스템을 파괴합니다! (정신력 -1)")
            st.rerun()

# [Stage 2]
elif st.session_state.stage == 'stage2':
    st.header("⛓️ 2단계: 암호 잠긴 메인프레임")
    st.write("컴퓨터 모니터에 암호 입력 창이 떠 있습니다.")
    st.write("**'해커의 무차별 대입 공격(Brute Force)을 막아낼 강력한 암호를 설정하라'**")
    
    pw_choice = st.selectbox("어떤 비밀번호를 선택하시겠습니까?", [
        "123456 (쉬운 연쇄 숫자)",
        "password123 (일반적인 단어 조합)",
        "P@ssw0rd!23# (대소문자, 숫자, 특수문자가 섞인 10자리 이상 암호)",
        "01012345678 (내 개인 전화번호)"
    ])
    
    if st.button("암호 제출 🔐", type="primary"):
        if "P@ssw0rd!23#" in pw_choice:
            st.session_state.sound_to_play = 'success'
            st.success("🎉 암호 통과! 복합 암호가 해커의 공격을 방어합니다.")
            st.session_state.inventory.append("💾 방화벽 칩")
            st.session_state.stage = 'stage3'
            st.rerun()
        else:
            st.session_state.sound_to_play = 'error'
            st.session_state.hp -= 1
            if st.session_state.hp <= 0:
                st.session_state.stage = 'game_over'
            else:
                st.error("💥 [틀렸습니다!] 해커가 1초 만에 비밀번호를 뚫었습니다! (정신력 -1)")
            st.rerun()

# [Stage 3]
elif st.session_state.stage == 'stage3':
    st.header("🚪 3단계: 백신 검사와 최종 탈출")
    st.write("탈출 문을 열려면 서버의 백신 검사를 완료해야 합니다.")
    
    action = st.radio("어떻게 서버를 정화하시겠습니까?", [
        "1. 정품 백신 프로그램을 업데이트하고 전체 시스템 정밀 검사를 실행한다.",
        "2. 어디서 주운 출처 불명의 USB를 서버에 꽂아본다.",
        "3. 바이러스 경고창이 떠도 무시하고 계속 '확인'을 누른다."
    ])
    
    if st.button("최종 실행 🩸", type="primary"):
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
                st.error("💥 [틀렸습니다!] 바이러스가 폭주하며 서버 전체가 오염되었습니다! (정신력 -1)")
            st.rerun()

# [게임 오버]
elif st.session_state.stage == 'game_over':
    st.session_state.sound_to_play = 'error'
    st.error("☠️ GAME OVER")
    st.title("💀 해커에게 시스템을 점령당했습니다...")
    st.write("정신력을 모두 잃었습니다. 다시 도전해서 탈출해보세요!")
    st.divider()
    
    if st.button("🔄 다시 도전하기", type="primary"):
        st.session_state.stage = 'intro'
        st.session_state.hp = 3
        st.session_state.inventory = []
        st.rerun()

# [탈출 성공]
elif st.session_state.stage == 'clear':
    st.balloons()
    st.title("🎉 탈출 성공!")
    st.write(f"**{st.session_state.player_name}**님은 모든 보안 위협을 이겨내고 성공적으로 탈출했습니다.")
    st.divider()
    
    st.subheader("📜 생존 인증서 발급")
    cert_img = generate_cert_image(st.session_state.player_name, st.session_state.hp)
    
    st.download_button(
        label="📸 생존 인증서(PNG) 다운로드",
        data=cert_img,
        file_name=f"{st.session_state.player_name}_생존인증서.png",
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
