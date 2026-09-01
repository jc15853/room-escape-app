import io
import os
import re
import requests
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# -----------------------------------------------------------------------------
# 0. 페이지 설정 및 세션 상태 초기화
# -----------------------------------------------------------------------------
st.set_page_config(page_title="사이버 피싱 검증소 💻", page_icon="🕵️‍♂️", layout="centered")

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
if 'quiz_index' not in st.session_state:
    st.session_state.quiz_index = 0

# -----------------------------------------------------------------------------
# 1. 상단 흰색 막대 제거 + 이메일 클라이언트 다크 테마 CSS
# -----------------------------------------------------------------------------
custom_css = """
<style>
    /* 상단 흰색 막대 및 헤더 제거 */
    header[data-testid="stHeader"], footer, div[data-testid="stDecoration"] {
        display: none !important;
    }

    /* 전체 배경: 깔끔한 다크 사이버 테마 */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* 타이틀 레드 강조 */
    h1, h2, h3 {
        color: #ff4d4d !important;
    }

    /* 이메일 클라이언트 박스 스타일링 */
    .email-container {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }

    .email-header {
        border-bottom: 1px solid #30363d;
        padding-bottom: 12px;
        margin-bottom: 15px;
        font-size: 0.95rem;
    }

    .email-header strong {
        color: #ff6666;
    }

    .email-sender-bad {
        color: #ff4d4d;
        background-color: #2a0000;
        padding: 2px 6px;
        border-radius: 4px;
        font-family: monospace;
    }

    .email-sender-good {
        color: #4dff88;
        background-color: #002a00;
        padding: 2px 6px;
        border-radius: 4px;
        font-family: monospace;
    }

    .email-body {
        background-color: #0d1117;
        border: 1px solid #21262d;
        border-radius: 6px;
        padding: 15px;
        line-height: 1.6;
        color: #e6edf3;
    }

    .fake-link {
        color: #58a6ff;
        text-decoration: underline;
        cursor: pointer;
        font-weight: bold;
    }

    .url-preview {
        background-color: #21262d;
        border: 1px solid #484f58;
        color: #ff7b72;
        padding: 6px 10px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.85rem;
        margin-top: 8px;
        display: inline-block;
    }

    /* 버튼 디자인 */
    .stButton > button {
        background-color: #21262d !important;
        color: #c9d1d9 !important;
        border: 1px solid #30363d !important;
        font-weight: bold;
        font-size: 1rem;
        padding: 12px 20px;
    }
    .stButton > button:hover {
        border-color: #ff4d4d !important;
        color: #ff4d4d !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 오디오 효과음 플레이어
# -----------------------------------------------------------------------------
SOUND_EFFECTS = {
    'error': 'https://assets.mixkit.co/active_storage/sfx/2572/2572-preview.mp3',   # 오답 피직음
    'success': 'https://assets.mixkit.co/active_storage/sfx/1435/1435-preview.mp3'  # 정답 띵동음
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
# 3. 생존 인증서 생성
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
    img = Image.new('RGB', (width, height), color='#0d1117')
    draw = ImageDraw.Draw(img)

    font_title = get_korean_font(22)
    font_sub = get_korean_font(13)
    font_body = get_korean_font(15)
    font_bold = get_korean_font(17)

    clean_name = remove_emojis(player_name) if player_name else "익명 보안관"

    draw.rectangle([(15, 15), (width-15, height-15)], outline='#ff4d4d', width=3)
    draw.rectangle([(30, 30), (width-30, 95)], fill='#161b22')
    draw.text((width//2, 52), "[ 피싱 분석관 자격 통과 ]", fill='#ff4d4d', font=font_title, anchor="mm")
    draw.text((width//2, 80), "GOOGLE PHISHING QUIZ BENCHMARK CLEARED", fill='#8b949e', font=font_sub, anchor="mm")

    draw.text((50, 140), f"검증된 분석관: {clean_name}", fill='#ffffff', font=font_bold)
    draw.text((50, 180), f"남은 정신력(HP): {'❤️' * remaining_hp} ({remaining_hp}/3)", fill='#ff6666', font=font_body)
    
    msg_lines = [
        "위 사람은 위장된 도메인, 교묘한 첨부파일(PDF/EXE),",
        "그리고 Google/교직원 사칭 피싱 메일을 정밀 분석하여",
        "사이버 피싱 공격을 완벽히 퇴치했음을 인증합니다."
    ]
    
    y_pos = 240
    for line in msg_lines:
        draw.text((50, y_pos), line, fill='#c9d1d9', font=font_body)
        y_pos += 30

    draw.rectangle([(width-200, height-100), (width-50, height-40)], outline='#ff4d4d', fill='#21262d')
    draw.text((width-125, height-70), "[ 검증 완료 ]", fill='#ff4d4d', font=font_bold, anchor="mm")

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

# -----------------------------------------------------------------------------
# 4. 구체적 피싱 데이터셋 (Google Phishing Quiz 참조)
# -----------------------------------------------------------------------------
PHISHING_STAGES = [
    {
        "title": "📧 1단계: Google 드라이브 공유 문서 알림",
        "sender": "Luke Weber <luke.weber@drive-secure-share.com>",
        "sender_real": False,
        "subject": "Luke Weber님이 '[2026_인센티브_계획안.pdf]' 문서를 공유했습니다.",
        "body": """
            안녕하세요,<br><br>
            Luke Weber님이 Google 드라이브를 통해 중요 문서를 공유했습니다.<br>
            아래 버튼을 눌러 문서를 확인하고 승인해 주세요.<br><br>
            <div style="text-align:center; margin:15px 0;">
                <span class="fake-link" style="background:#1a73e8; color:white; padding:10px 20px; border-radius:4px; text-decoration:none;">Google 드라이브에서 문서 열기</span>
            </div>
        """,
        "hover_url": "https://drive-secure-share.com/login?redirect=google.com",
        "is_phishing": True,
        "explanation": "보낸 사람 주소가 <code>google.com</code>이 아닌 <code>drive-secure-share.com</code>이며, 링크 연결 주소 역시 교묘하게 본뜬 피싱 도메인입니다!"
    },
    {
        "title": "📧 2단계: 대학/회사 전산팀의 용량 초과 경고",
        "sender": "IT 지원팀 <admin@my-university.ac.kr>",
        "sender_real": True,
        "subject": "[긴급] 사내 이메일 계정 용량 초과 안내 (99% 사용 중)",
        "body": """
            회원님의 이메일 사물함 용량이 99%에 도달했습니다.<br>
            오늘 이내로 용량을 증설하지 않으면 메일 수발신이 중단됩니다.<br><br>
            전산실 공식 페이지에서 용량 무료 신청을 진행해주세요.<br>
            <span class="fake-link">https://my-university.ac.kr/storage/expand</span>
        """,
        "hover_url": "https://my-university.ac.kr/storage/expand",
        "is_phishing": False,
        "explanation": "보낸 사람 도메인이 정품 <code>my-university.ac.kr</code>과 일치하며, 링크 실제 연결 주소도 변경 없이 동일한 공식 내부 페이지입니다. (정상 메일)"
    },
    {
        "title": "📧 3단계: 팩스 수신 알림 및 첨부파일",
        "sender": "e-Fax 서비스 <efax-notice@mail-service-center.net>",
        "sender_real": False,
        "subject": "[수신 완료] 전자팩스 문서가도착했습니다 (Ref: #89201)",
        "body": """
            고객님께 새 전자팩스가 도착했습니다.<br><br>
            <b>- 발신 번호:</b> 02-1234-****<br>
            <b>- 첨부파일:</b> <span class="fake-link">📄 Fax_Document_2026.pdf.exe</span> (1.2MB)<br><br>
            첨부된 PDF 파일을 내려받아 확인하세요.
        """,
        "hover_url": "https://mail-service-center.net/downloads/Fax_Document_2026.pdf.exe",
        "is_phishing": True,
        "explanation": "파일 이름이 <code>.pdf.exe</code>로 이중 확장자를 사용 중입니다! 문서로 위장한 이중 확장자 실행파일(.exe)은 100% 악성 바이러스입니다."
    }
]

# -----------------------------------------------------------------------------
# 5. 상단 상태바 및 효과음
# -----------------------------------------------------------------------------
if st.session_state.stage not in ['intro', 'game_over', 'clear']:
    col_status1, col_status2 = st.columns([2, 1])
    with col_status1:
        st.caption(f"🕵️‍♂️ 분석관: **{st.session_state.player_name}** | 📊 진척도: ({st.session_state.quiz_index + 1}/{len(PHISHING_STAGES)})")
    with col_status2:
        st.markdown(f"🖤 정신력(HP): **{'❤️' * st.session_state.hp}** ({st.session_state.hp}/3)")
    st.divider()

if st.session_state.sound_to_play:
    play_sound(st.session_state.sound_to_play)
    st.session_state.sound_to_play = None

# -----------------------------------------------------------------------------
# 6. 화면 흐름
# -----------------------------------------------------------------------------

# [시작 화면]
if st.session_state.stage == 'intro':
    st.title("🕵️‍♂️ 피싱 바이러스 감옥: 구글 분석 스타일")
    st.subheader("진짜 메일과 피싱 메일을 정밀 분석하여 감옥을 탈출하라!")
    st.write("실제 해커들은 구글 서비스, 대학 전산실, 팩스 알림 등을 완벽히 사칭합니다.")
    st.write("보낸 사람의 **이메일 주소**, **버튼 위로 마우스를 올렸을 때의 실제 URL**, **첨부파일 확장자**를 세밀하게 관찰하세요.")
    st.divider()
    
    name_input = st.text_input("분석관 이름을 입력하세요:", value="김보안")
    
    if st.button("피싱 검증 시작하기 🔓", type="primary", use_container_width=True):
        if name_input.strip():
            st.session_state.player_name = name_input.strip()
            st.session_state.stage = 'quiz'
            st.session_state.quiz_index = 0
            st.rerun()
        else:
            st.warning("이름을 입력해야 분석실에 진입할 수 있습니다.")

# [퀴즈 진행 화면]
elif st.session_state.stage == 'quiz':
    current_q = PHISHING_STAGES[st.session_state.quiz_index]
    
    st.header(current_q["title"])
    st.write("아래 수신된 메일을 자세히 살펴보고, 이것이 **[피싱 메일]**인지 **[정상 메일]**인지 판별하세요.")
    
    # 이메일 클라이언트 UI 모사
    sender_class = "email-sender-bad" if not current_q["sender_real"] else "email-sender-good"
    
    email_html = f"""
    <div class="email-container">
        <div class="email-header">
            <div><strong>보낸사람:</strong> <span class="{sender_class}">{current_q['sender']}</span></div>
            <div style="margin-top:6px;"><strong>제목:</strong> {current_q['subject']}</div>
        </div>
        <div class="email-body">
            {current_q['body']}
        </div>
        <div style="margin-top: 15px;">
            <span style="font-size:0.85rem; color:#8b949e;">🔍 링크 hover / 실제 연결 대상 주소:</span><br>
            <div class="url-preview">🔗 {current_q['hover_url']}</div>
        </div>
    </div>
    """
    st.markdown(email_html, unsafe_allow_html=True)
    
    st.markdown("#### 이 메일은 안전합니까, 아니면 피싱입니까?")
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("✅ 정상 메일이다 (안전)", use_container_width=True):
            user_phishing_choice = False
            # 정답 검증
            if user_phishing_choice == current_q["is_phishing"]:
                st.session_state.sound_to_play = 'success'
                st.success(f"🎉 **정답입니다!**\n\n{current_q['explanation']}")
                if st.session_state.quiz_index + 1 < len(PHISHING_STAGES):
                    st.session_state.quiz_index += 1
                    st.rerun()
                else:
                    st.session_state.stage = 'clear'
                    st.rerun()
            else:
                st.session_state.sound_to_play = 'error'
                st.session_state.hp -= 1
                if st.session_state.hp <= 0:
                    st.session_state.stage = 'game_over'
                else:
                    st.error(f"💥 **오답! 피싱 메일입니다!** (정신력 -1)\n\n{current_q['explanation']}")
                st.rerun()

    with col_btn2:
        if st.button("🚨 피싱 메일이다 (위험)", use_container_width=True):
            user_phishing_choice = True
            # 정답 검증
            if user_phishing_choice == current_q["is_phishing"]:
                st.session_state.sound_to_play = 'success'
                st.success(f"🎉 **정답입니다!**\n\n{current_q['explanation']}")
                if st.session_state.quiz_index + 1 < len(PHISHING_STAGES):
                    st.session_state.quiz_index += 1
                    st.rerun()
                else:
                    st.session_state.stage = 'clear'
                    st.rerun()
            else:
                st.session_state.sound_to_play = 'error'
                st.session_state.hp -= 1
                if st.session_state.hp <= 0:
                    st.session_state.stage = 'game_over'
                else:
                    st.error(f"💥 **오답! 이것은 정상 메일입니다!** (정신력 -1)\n\n{current_q['explanation']}")
                st.rerun()

# [게임 오버]
elif st.session_state.stage == 'game_over':
    st.session_state.sound_to_play = 'error'
    st.error("☠️ PHISHING ATTACK DETECTED: ACCESS DENIED")
    st.title("💀 해커에게 계정을 탈취당했습니다...")
    st.write("교묘한 피싱 트랩을 간파하지 못했습니다. 다시 분석 연습을 진행해보세요.")
    st.divider()
    
    if st.button("🔄 재도전하기", type="primary", use_container_width=True):
        st.session_state.stage = 'intro'
        st.session_state.hp = 3
        st.session_state.quiz_index = 0
        st.rerun()

# [탈출 성공]
elif st.session_state.stage == 'clear':
    st.balloons()
    st.title("🎉 피싱 검증 완료 & 감옥 탈출 성공!")
    st.write(f"**{st.session_state.player_name}** 분석관님은 모든 피싱 공작을 구별해냈습니다.")
    st.divider()
    
    st.subheader("📜 피싱 분석관 생존 자격증")
    cert_img = generate_cert_image(st.session_state.player_name, st.session_state.hp)
    
    st.download_button(
        label="📸 자격증(PNG) 다운로드",
        data=cert_img,
        file_name=f"{st.session_state.player_name}_피싱분석자격증.png",
        mime="image/png",
        type="primary",
        use_container_width=True
    )
    
    st.divider()
    if st.button("🔄 처음으로 돌아가기", use_container_width=True):
        st.session_state.stage = 'intro'
        st.session_state.hp = 3
        st.session_state.quiz_index = 0
        st.rerun()
