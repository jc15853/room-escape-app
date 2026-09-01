import io
import os
import re
import requests
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# -----------------------------------------------------------------------------
# 0. 페이지 설정 및 세션 상태 초기화
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="사이버 탐정 사무소: 보안 위협 분석관 🕵️‍♂️",
    page_icon="🕵️‍♂️",
    layout="centered"
)

if 'stage' not in st.session_state:
    st.session_state.stage = 'intro'
if 'hp' not in st.session_state:
    st.session_state.hp = 3
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'player_name' not in st.session_state:
    st.session_state.player_name = ""
if 'quiz_index' not in st.session_state:
    st.session_state.quiz_index = 0
if 'sound_to_play' not in st.session_state:
    st.session_state.sound_to_play = None

# -----------------------------------------------------------------------------
# 1. 커스텀 CSS (다크 사이버 테마 & 이메일/의뢰서 뷰어)
# -----------------------------------------------------------------------------
custom_css = """
<style>
    /* 헤더 및 푸터 숨김 */
    header[data-testid="stHeader"], footer, div[data-testid="stDecoration"] {
        display: none !important;
    }

    /* 전체 테마 설정 */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    h1, h2, h3 {
        color: #58a6ff !important;
    }

    /* 의뢰서 / 이메일 박스 스타일 */
    .case-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    }

    .case-header {
        border-bottom: 1px solid #30363d;
        padding-bottom: 12px;
        margin-bottom: 15px;
        font-size: 0.95rem;
    }

    .sender-phishing {
        color: #ff7b72;
        background-color: #3c1e1e;
        padding: 3px 8px;
        border-radius: 4px;
        font-family: monospace;
    }

    .sender-safe {
        color: #7ee787;
        background-color: #1e3c27;
        padding: 3px 8px;
        border-radius: 4px;
        font-family: monospace;
    }

    .case-body {
        background-color: #0d1117;
        border: 1px solid #21262d;
        border-radius: 8px;
        padding: 15px;
        line-height: 1.6;
        color: #f0f6fc;
        margin-bottom: 15px;
    }

    .evidence-box {
        background-color: #1c2128;
        border-left: 4px solid #f85149;
        color: #ff7b72;
        padding: 12px 15px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.9rem;
    }

    /* 버튼 스타일 */
    .stButton > button {
        background-color: #21262d !important;
        color: #c9d1d9 !important;
        border: 1px solid #363b42 !important;
        font-weight: bold;
        font-size: 1rem;
        padding: 12px 20px;
        border-radius: 8px;
    }
    .stButton > button:hover {
        border-color: #58a6ff !important;
        color: #58a6ff !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 효과음 및 오디오 재생 함수
# -----------------------------------------------------------------------------
SOUND_EFFECTS = {
    'error': 'https://assets.mixkit.co/active_storage/sfx/2572/2572-preview.mp3',
    'success': 'https://assets.mixkit.co/active_storage/sfx/1435/1435-preview.mp3'
}

def play_sound(sound_key):
    sound_url = SOUND_EFFECTS.get(sound_key)
    if sound_url:
        sound_html = f"""
            <audio autoplay style="display:none">
                <source src="{sound_url}" type="audio/mpeg">
            </audio>
        """
        st.components.v1.html(sound_html, height=0)

# -----------------------------------------------------------------------------
# 3. 인증서 생성 로직 (나눔고딕 폰트 자동 로드)
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

def generate_cert_image(player_name, remaining_hp, score):
    width, height = 650, 480
    img = Image.new('RGB', (width, height), color='#0d1117')
    draw = ImageDraw.Draw(img)

    font_title = get_korean_font(22)
    font_sub = get_korean_font(13)
    font_body = get_korean_font(15)
    font_bold = get_korean_font(17)

    clean_name = remove_emojis(player_name) if player_name else "익명 수사관"

    # 테두리 및 헤더
    draw.rectangle([(15, 15), (width-15, height-15)], outline='#58a6ff', width=3)
    draw.rectangle([(30, 30), (width-30, 95)], fill='#161b22')
    draw.text((width//2, 52), "[ 사이버 보안 수사관 임명장 ]", fill='#58a6ff', font=font_title, anchor="mm")
    draw.text((width//2, 80), "CYBER SECURITY INVESTIGATOR CERTIFICATE", fill='#8b949e', font=font_sub, anchor="mm")

    # 내용 입력
    draw.text((50, 130), f"수 사 관 명: {clean_name}", fill='#ffffff', font=font_bold)
    draw.text((50, 165), f"남은 체력: {'❤️' * remaining_hp} ({remaining_hp}/3)", fill='#ff7b72', font=font_body)
    draw.text((50, 195), f"최종 분석 점수: {score}점", fill='#7ee787', font=font_body)
    
    msg_lines = [
        "위 사람은 위장 도메인, 출처 불분명한 첨부파일,",
        "그리고 사회공학적 피싱 메일을 정밀 분석하여",
        "사이버 침해 사고를 성공적으로 예방했음을 인증합니다."
    ]
    
    y_pos = 250
    for line in msg_lines:
        draw.text((50, y_pos), line, fill='#c9d1d9', font=font_body)
        y_pos += 28

    draw.rectangle([(width-210, height-90), (width-40, height-35)], outline='#58a6ff', fill='#21262d')
    draw.text((width-125, height-62), "[ 검증 승인 완료 ]", fill='#58a6ff', font=font_bold, anchor="mm")

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

# -----------------------------------------------------------------------------
# 4. 사건 데이터셋 (깔끔한 HTML 구조 유지)
# -----------------------------------------------------------------------------
STORY_STAGES = [
    {
        "case_no": "사건 #01",
        "title": "📂 공유 문서 출처 분석 의뢰",
        "sender": "보안팀 <security-alert@drive-check-login.com>",
        "sender_is_safe": False,
        "subject": "[긴급] 사내 보안 지침 개정안 공유 문서를 확인하세요",
        "body": "안녕하세요 직원 여러분,<br><br>이번 분기 신규 보안 지침 문서가 Google 드라이브로 공유되었습니다.<br>아래 링크를 통해 로그인 후 문서를 열람해주시기 바랍니다.<br><br><div style='text-align:center; margin:12px 0;'><span style='background:#1f6beb; color:white; padding:8px 16px; border-radius:4px;'>문서 바로가기</span></div>",
        "evidence": "🔗 마우스 연결 예상 주소: https://drive-check-login.com/auth/login",
        "is_phishing": True,
        "explanation": "보낸 사람의 도메인이 공식 회사 도메인이 아닌 외부 피싱 도메인(drive-check-login.com)입니다!"
    },
    {
        "case_no": "사건 #02",
        "title": "📧 중앙 도서관 대출 안내",
        "sender": "중앙도서관 <lib-notice@school.ac.kr>",
        "sender_is_safe": True,
        "subject": "[안내] 대출하신 도서의 반납 예정일 안내입니다.",
        "body": "회원님, 대출하신 도서 [파이썬 프로그래밍 기초]의 반납 예정일이 2일 남았습니다.<br>연장을 원하시면 도서관 홈페이지의 [나의 이용현황]에서 신청해주세요.",
        "evidence": "🔗 링크 주소: https://school.ac.kr/library/mypage",
        "is_phishing": False,
        "explanation": "학교 공식 도메인(school.ac.kr)을 사용 중이며 불필요한 개인정보 입력이나 외부 다운로드를 요구하지 않는 정상 안내 메일입니다."
    },
    {
        "case_no": "사건 #03",
        "title": "⚠️ 긴급 첨부파일 검증",
        "sender": "발주담당자 <order-dept@global-supply.net>",
        "sender_is_safe": False,
        "subject": "[견적서] 요청하신 부품 견적서 및 세금계산서 첨부",
        "body": "요청하신 견적서 송부드립니다.<br>첨부된 압축파일을 해제한 뒤 확인 부탁드립니다.<br><br><b>- 첨부파일:</b> <span style='color:#58a6ff; text-decoration:underline;'>📄 2026_Estimate_Invoice.pdf.exe</span> (1.8MB)",
        "evidence": "📁 첨부파일 확장자: .pdf.exe (실행 파일)",
        "is_phishing": True,
        "explanation": "문서 파일(.pdf)처럼 보이지만 실제로는 실행 파일(.exe)인 이중 확장자 악성코드 트랩입니다!"
    }
]

# -----------------------------------------------------------------------------
# 5. 상단 상태바 및 효과음 재생
# -----------------------------------------------------------------------------
if st.session_state.stage not in ['intro', 'game_over', 'clear']:
    col_status1, col_status2 = st.columns([2, 1])
    with col_status1:
        st.caption(f"🕵️ 수사관: **{st.session_state.player_name}** | 📊 사건: ({st.session_state.quiz_index + 1}/{len(STORY_STAGES)})")
    with col_status2:
        st.markdown(f"❤️ 체력: **{'❤️' * st.session_state.hp}** ({st.session_state.hp}/3)")
    st.divider()

if st.session_state.sound_to_play:
    play_sound(st.session_state.sound_to_play)
    st.session_state.sound_to_play = None

# -----------------------------------------------------------------------------
# 6. 메인 화면 흐름 제어
# -----------------------------------------------------------------------------

# [1] 시작 화면
if st.session_state.stage == 'intro':
    st.title("🕵️‍♂️ 사이버 탐정 사무소: 피싱 수사관")
    st.subheader("수상한 이메일과 의뢰서를 분석하여 피싱 트랩을 간파하세요!")
    st.write("의심스러운 **보낸 사람 주소**, **실제 연결 URL**, **첨부파일의 진짜 확장자**를 정밀하게 조사해야 합니다.")
    st.divider()
    
    name_input = st.text_input("수사관 이름을 입력하세요:", value="김탐정")
    
    if st.button("수사 시작하기 🔍", type="primary", use_container_width=True):
        if name_input.strip():
            st.session_state.player_name = name_input.strip()
            st.session_state.stage = 'quiz'
            st.session_state.quiz_index = 0
            st.session_state.hp = 3
            st.session_state.score = 0
            st.rerun()
        else:
            st.warning("수사관 이름을 입력해주세요.")

# [2] 사건 분석 (퀴즈 진행)
elif st.session_state.stage == 'quiz':
    current_case = STORY_STAGES[st.session_state.quiz_index]
    
    st.caption(current_case["case_no"])
    st.header(current_case["title"])
    
    sender_style = "sender-phishing" if not current_case["sender_is_safe"] else "sender-safe"
    
    # 렌더링 오류를 완전히 방지한 깔끔한 HTML 매핑
    case_html = f"""<div class="case-card">
    <div class="case-header">
        <div><strong>보낸 사람:</strong> <span class="{sender_style}">{current_case['sender']}</span></div>
        <div style="margin-top:6px;"><strong>제목:</strong> {current_case['subject']}</div>
    </div>
    <div class="case-body">
        {current_case['body']}
    </div>
    <div class="evidence-box">
        🔍 <strong>단서 포착:</strong> {current_case['evidence']}
    </div>
</div>"""

    st.markdown(case_html, unsafe_allow_html=True)
    
    st.markdown("#### 🧐 수사관 판정: 이 메일은 안전합니까?")
    
    col_btn1, col_btn2 = st.columns(2)
    
    # [안전 메일 판정]
    with col_btn1:
        if st.button("✅ 안전한 메일이다", use_container_width=True):
            user_choice_is_phishing = False
            if user_choice_is_phishing == current_case["is_phishing"]:
                st.session_state.sound_to_play = 'success'
                st.session_state.score += 100
                st.success(f"🎉 **정확한 분석입니다!**\n\n{current_case['explanation']}")
                
                if st.session_state.quiz_index + 1 < len(STORY_STAGES):
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
                    st.error(f"💥 **분석 실패! 피싱 트랩에 걸렸습니다!** (체력 -1)\n\n{current_case['explanation']}")
                st.rerun()

    # [피싱 메일 판정]
    with col_btn2:
        if st.button("🚨 피싱 트랩이다", use_container_width=True):
            user_choice_is_phishing = True
            if user_choice_is_phishing == current_case["is_phishing"]:
                st.session_state.sound_to_play = 'success'
                st.session_state.score += 100
                st.success(f"🎉 **정확한 분석입니다!**\n\n{current_case['explanation']}")
                
                if st.session_state.quiz_index + 1 < len(STORY_STAGES):
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
                    st.error(f"💥 **오판! 이것은 정상적인 메일이었습니다!** (체력 -1)\n\n{current_case['explanation']}")
                st.rerun()

# [3] 게임 오버
elif st.session_state.stage == 'game_over':
    st.error("☠️ SYSTEM COMPROMISED")
    st.title("💀 악성 코드 감염 및 수사 실패...")
    st.write("피싱 공격을 간파하지 못해 시스템 통제권을 상실했습니다. 다시 도전해보세요.")
    st.divider()
    
    if st.button("🔄 재수사 시작하기", type="primary", use_container_width=True):
        st.session_state.stage = 'intro'
        st.session_state.hp = 3
        st.session_state.quiz_index = 0
        st.rerun()

# [4] 사건 해결 (클리어)
elif st.session_state.stage == 'clear':
    st.balloons()
    st.title("🏆 모든 피싱 사건 해결 성공!")
    st.write(f"**{st.session_state.player_name}** 수사관님은 모든 피싱 공작을 완벽하게 차단했습니다.")
    st.divider()
    
    st.subheader("📜 사이버 보안 수사관 임명장")
    cert_img = generate_cert_image(
        st.session_state.player_name,
        st.session_state.hp,
        st.session_state.score
    )
    
    st.download_button(
        label="📸 수사관 임명장(PNG) 다운로드",
        data=cert_img,
        file_name=f"{st.session_state.player_name}_수사관임명장.png",
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
