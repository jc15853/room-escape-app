import io
import os
import re
import requests
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# -----------------------------------------------------------------------------
# 0. 페이지 설정 및 세션 상태(Session State) 초기화
# -----------------------------------------------------------------------------
st.set_page_config(page_title="보안 해커의 방 탈출 🕵️‍♂️", page_icon="🔐", layout="centered")

# 게임 진행 단계(stage), 체력(hp), 획득 아이템, 사용자 이름
if 'stage' not in st.session_state:
    st.session_state.stage = 'intro'
if 'hp' not in st.session_state:
    st.session_state.hp = 3
if 'inventory' not in st.session_state:
    st.session_state.inventory = []
if 'player_name' not in st.session_state:
    st.session_state.player_name = ""

# -----------------------------------------------------------------------------
# 1. 폰트 및 유틸리티 함수
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

# 탈출 성공 인증서 PNG 생성 함수
def generate_cert_image(player_name, remaining_hp):
    width, height = 650, 500
    img = Image.new('RGB', (width, height), color='#FFFFFF')
    draw = ImageDraw.Draw(img)

    font_title = get_korean_font(24)
    font_sub = get_korean_font(14)
    font_body = get_korean_font(16)
    font_bold = get_korean_font(18)

    clean_name = remove_emojis(player_name) if player_name else "익명 보안관"

    # 외곽 테두리 및 헤더
    draw.rectangle([(15, 15), (width-15, height-15)], outline='#10B981', width=4)
    draw.rectangle([(30, 30), (width-30, 95)], fill='#ECFDF5')
    draw.text((width//2, 52), "[디지털 보안 해커 방 탈출 성공]", fill='#047857', font=font_title, anchor="mm")
    draw.text((width//2, 80), "사이버 보안 마스터 인증서", fill='#059669', font=font_sub, anchor="mm")

    # 본문 내용
    draw.text((50, 140), f"요원 이름: {clean_name}", fill='#1F2937', font=font_bold)
    draw.text((50, 180), f"남은 보안 체력: {'❤️' * remaining_hp} ({remaining_hp}/3)", fill='#1F2937', font=font_body)
    
    msg_lines = [
        "위 요원은 피싱 문자 구분, 안전한 비밀번호 설정,",
        "그리고 악성 코드 바이러스 퇴치 미션을 완벽히 수행하여",
        "해커의 가상 서버 방을 성공적으로 탈출했음을 인증합니다."
    ]
    
    y_pos = 240
    for line in msg_lines:
        draw.text((50, y_pos), line, fill='#374151', font=font_body)
        y_pos += 30

    # 직인 박스
    draw.rectangle([(width-200, height-100), (width-50, height-40)], outline='#10B981', fill='#F0FDF4')
    draw.text((width-125, height-70), "[보안 마스터]", fill='#047857', font=font_bold, anchor="mm")

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

# -----------------------------------------------------------------------------
# 2. 게임 상태 관리 공통 UI (상단 상태바)
# -----------------------------------------------------------------------------
if st.session_state.stage not in ['intro', 'game_over', 'clear']:
    col_status1, col_status2 = st.columns([2, 1])
    with col_status1:
        st.caption(f"👤 요원: **{st.session_state.player_name}** | 🎒 가방: {', '.join(st.session_state.inventory) if st.session_state.inventory else '비어있음'}")
    with col_status2:
        st.markdown(f"❤️ 보안 체력: **{'❤️' * st.session_state.hp}** ({st.session_state.hp}/3)")
    st.divider()

# -----------------------------------------------------------------------------
# 3. 스토리 및 스테이지 흐름 (If-Elif 알고리즘)
# -----------------------------------------------------------------------------

# [시작 화면]
if st.session_state.stage == 'intro':
    st.title("🕵️‍♂️ 해커의 디지털 서버실 탈출기")
    st.subheader("수상한 이메일을 열람했다가 해커의 가상 공간에 갇혔다!")
    st.write("안전한 디지털 윤리와 보안 지식을 활용해 문제를 풀고 방을 탈출하세요.")
    st.divider()
    
    name_input = st.text_input("당신의 요원 이름을 입력하세요:", value="김보안")
    
    if st.button("게임 시작하기 🚀", type="primary", use_container_width=True):
        if name_input.strip():
            st.session_state.player_name = name_input.strip()
            st.session_state.stage = 'stage1'
            st.rerun()
        else:
            st.warning("이름을 입력해야 시작할 수 있습니다!")

# [Stage 1: 피싱 문자 구분하기]
elif st.session_state.stage == 'stage1':
    st.header("1️⃣ 첫 번째 관문: 의심스러운 스마트폰")
    st.write("해커의 책상 위에 스마트폰이 놓여 있습니다. 알림 창에 문자 메시지가 도착했습니다.")
    
    st.info("📱 **[문자 내용]**\n\n'[국외발신] 택배 배송 오류로 주소지 확인이 필요합니다. 아래 링크를 눌러 앱을 설치하세요: http://bit.ly/fake_link'")
    
    st.markdown("#### 어떻게 행동하시겠습니까?")
    
    choice = st.radio("선택지를 고르세요:", [
        "1. 택배가 안 올까봐 얼른 링크를 클릭해서 설치한다.",
        "2. 스미싱(피싱) 문자로 의심하고 링크를 누르지 않은 채 삭제한다.",
        "3. 친구에게 이 링크를 공유해서 대신 확인해달라고 한다."
    ])
    
    if st.button("선택 완료 ➡️", type="primary"):
        if "2." in choice:
            st.success("🎉 정답입니다! 출처가 불분명한 URL 및 앱 설치 링크는 절대 누르면 안 됩니다.")
            st.session_state.inventory.append("🗝️ 보안 열쇠")
            st.session_state.stage = 'stage2'
            st.rerun()
        else:
            st.error("💥 악성 앱이 설치되어 스마트폰이 감염되었습니다! (체력 -1)")
            st.session_state.hp -= 1
            if st.session_state.hp <= 0:
                st.session_state.stage = 'game_over'
            st.rerun()

# [Stage 2: 안전한 비밀번호 설정]
elif st.session_state.stage == 'stage2':
    st.header("2️⃣ 두 번째 관문: 암호 잠긴 노트북")
    st.write("노트북 전원을 켰더니 해커의 방을 나가는 암호를 입력하라고 합니다.")
    st.write("힌트 노트에는 **'해커가 추측하기 가장 어려운, 가장 안전한 비밀번호 형식'**이 암호라고 적혀있습니다.")
    
    pw_choice = st.selectbox("어떤 비밀번호를 선택하시겠습니까?", [
        "123456 (연속된 숫자로 이루어진 암호)",
        "password123 (영단어와 쉬운 숫자의 조합)",
        "P@ssw0rd!23# (영문 대소문자, 숫자, 특수문자가 8자리 이상 섞인 조합)",
        "01012345678 (내 전화번호)"
    ])
    
    if st.button("암호 입력 🔓", type="primary"):
        if "P@ssw0rd!23#" in pw_choice:
            st.success("🎉 노트북이 열렸습니다! 영문, 숫자, 특수문자를 혼합한 복잡한 비밀번호가 안전합니다.")
            st.session_state.inventory.append("💾 백업 USB")
            st.session_state.stage = 'stage3'
            st.rerun()
        else:
            st.error("💥 해커가 너무 쉽게 암호를 대조해 해킹에 성공했습니다! (체력 -1)")
            st.session_state.hp -= 1
            if st.session_state.hp <= 0:
                st.session_state.stage = 'game_over'
            st.rerun()

# [Stage 3: 백신 및 방화벽 작동]
elif st.session_state.stage == 'stage3':
    st.header("3️⃣ 마지막 관문: 메인 서버실 문")
    st.write("탈출 문 앞에 도착했습니다. 문을 열려면 메인 컨트롤러에 백신 프로그램을 실행해야 합니다.")
    st.write("주변에서 획득한 아이템이 비상 탈출을 돕습니다.")
    
    st.write(f"현재 보유한 아이템: **{', '.join(st.session_state.inventory)}**")
    
    action = st.radio("어떤 조치를 취하시겠습니까?", [
        "1. 백신 프로그램을 업데이트하고 정밀 검사를 실행한다.",
        "2. 출처를 알 수 없는 USB 프로그램을 그냥 메인 서버에 꽂는다.",
        "3. 경고창이 떠도 '허용'을 계속 누른다."
    ])
    
    if st.button("최종 실행 🚪", type="primary"):
        if "1." in action:
            st.session_state.stage = 'clear'
            st.rerun()
        else:
            st.error("💥 바이러스가 서버 전체로 유포되어 서버실이 잠겼습니다! (체력 -1)")
            st.session_state.hp -= 1
            if st.session_state.hp <= 0:
                st.session_state.stage = 'game_over'
            st.rerun()

# [게임 오버]
elif st.session_state.stage == 'game_over':
    st.error("☠️ GAME OVER")
    st.subheader("보안 체력이 모두 소진되어 해커에게 잡혔습니다!")
    st.write("디지털 보안 수칙을 다시 확인하고 재도전해 보세요.")
    st.divider()
    
    if st.button("🔄 처음부터 다시 도전하기", type="primary"):
        st.session_state.stage = 'intro'
        st.session_state.hp = 3
        st.session_state.inventory = []
        st.rerun()

# [탈출 성공 / 클리어]
elif st.session_state.stage == 'clear':
    st.balloons()
    st.success("🎉 탈출 성공! 🎉")
    st.title("🏆 축하합니다! 모든 보안 관문을 통과하셨습니다.")
    st.write(f"요원 **{st.session_state.player_name}**님은 뛰어난 디지털 윤리 지식으로 해커의 서버를 무사히 탈출했습니다.")
    st.divider()
    
    st.subheader("📜 탈출 성공 인증서 받기")
    cert_img = generate_cert_image(st.session_state.player_name, st.session_state.hp)
    
    st.download_button(
        label="📸 탈출 성공 인증서(PNG) 다운로드",
        data=cert_img,
        file_name=f"{st.session_state.player_name}_탈출인증서.png",
        mime="image/png",
        type="primary",
        use_container_width=True
    )
    
    st.divider()
    if st.button("🔄 게임 처음으로 돌리기"):
        st.session_state.stage = 'intro'
        st.session_state.hp = 3
        st.session_state.inventory = []
        st.rerun()
