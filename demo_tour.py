"""
Demo Tour Module - Inline Guide Version
Streamlit 네이티브 방식으로 구현된 튜토리얼 시스템
"""
import streamlit as st

# 총 5단계
TOTAL_STEPS = 5

# 단계별 콘텐츠
TOUR_CONTENT = {
    1: {
        "title": "🔑 Step 1: API 키 설정",
        "desc": "AI 기능을 사용하려면 Gemini API 키가 필요합니다. 사이드바의 'Gemini API Key' 입력란에 키를 입력하세요.",
        "target": "api_key"
    },
    2: {
        "title": "📝 Step 2: 행사 정보 입력",
        "desc": "기사를 작성할 행사의 기본 정보(학년, 행사명, 장소, 분위기 등)를 입력하세요.",
        "target": "event_form"
    },
    3: {
        "title": "✨ Step 3: AI 초안 생성",
        "desc": "정보 입력이 끝나면 하단의 '기사 초안 생성하기' 버튼을 클릭하세요. AI가 자동으로 기사를 작성합니다.",
        "target": "generate_button"
    },
    4: {
        "title": "🗂️ Step 4: 기사 보관함",
        "desc": "작성된 기사들은 '보관함 및 뉴스레터' 메뉴에서 확인할 수 있습니다. 목록에서 기사를 선택해보세요.",
        "target": "archive_list"
    },
    5: {
        "title": "📰 Step 5: 뉴스레터 발행",
        "desc": "여러 기사를 선택하고 '통합 문서 생성' 버튼을 누르면 PDF, Word, PPT 파일을 한 번에 만들 수 있습니다.",
        "target": "newsletter_button"
    }
}


def init_demo_mode():
    """데모 모드 상태 초기화"""
    if "demo_mode" not in st.session_state:
        st.session_state.demo_mode = False
    if "demo_step" not in st.session_state:
        st.session_state.demo_step = 0


def start_demo():
    """데모 시작"""
    from demo_data import load_demo_data_to_db
    from engines.db_service import DatabaseService
    
    st.session_state.demo_mode = True
    st.session_state.demo_step = 1
    load_demo_data_to_db(DatabaseService())
    st.rerun()


def exit_demo():
    """데모 종료"""
    from demo_data import clear_demo_data_from_db
    from engines.db_service import DatabaseService
    
    st.session_state.demo_mode = False
    st.session_state.demo_step = 0
    clear_demo_data_from_db(DatabaseService())
    st.rerun()


def next_step():
    """다음 단계로 이동 (최대 5단계)"""
    if st.session_state.demo_step < TOTAL_STEPS:
        st.session_state.demo_step += 1
    else:
        # 마지막 단계에서 다음 누르면 완료 처리
        st.session_state.demo_step = TOTAL_STEPS + 1  # 완료 상태


def prev_step():
    """이전 단계로 이동"""
    if st.session_state.demo_step > 1:
        st.session_state.demo_step -= 1


def get_current_step():
    """현재 단계 반환 (1~5, 6=완료)"""
    return st.session_state.get("demo_step", 0)


def is_demo_active():
    """데모 모드 활성화 여부"""
    return st.session_state.get("demo_mode", False)


def is_tour_complete():
    """투어 완료 여부"""
    return get_current_step() > TOTAL_STEPS


def should_highlight(target_name):
    """특정 영역이 현재 단계에서 강조되어야 하는지"""
    if not is_demo_active():
        return False
    
    step = get_current_step()
    if step < 1 or step > TOTAL_STEPS:
        return False
    
    return TOUR_CONTENT[step]["target"] == target_name


def render_sidebar_demo_button():
    """사이드바 데모 버튼 및 네비게이션"""
    init_demo_mode()
    
    if not is_demo_active():
        # 시작 버튼
        st.markdown("---")
        st.markdown("##### 🚀 처음이신가요?")
        if st.button("✨ 튜토리얼 시작", type="primary", use_container_width=True):
            start_demo()
    else:
        step = get_current_step()
        
        if is_tour_complete():
            # 완료 상태
            st.success("✅ 튜토리얼 완료!")
            if st.button("🏠 튜토리얼 종료", use_container_width=True):
                exit_demo()
        else:
            # 진행 중
            st.info(f"📍 진행 중: {step} / {TOTAL_STEPS}")
            
            # 네비게이션 버튼
            col1, col2 = st.columns(2)
            with col1:
                if step > 1:
                    if st.button("◀ 이전", use_container_width=True):
                        prev_step()
                        st.rerun()
            with col2:
                btn_label = "다음 ▶" if step < TOTAL_STEPS else "완료 ✓"
                if st.button(btn_label, use_container_width=True, type="primary"):
                    next_step()
                    st.rerun()
            
            # 종료 버튼
            if st.button("🚪 튜토리얼 종료", use_container_width=True):
                exit_demo()


def render_guide_panel():
    """메인 화면 상단에 안내 패널 표시"""
    if not is_demo_active():
        return
    
    step = get_current_step()
    
    # 완료 모달
    if is_tour_complete():
        st.markdown("""
            <style>
            .completion-box {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 16px;
                text-align: center;
                margin-bottom: 24px;
            }
            .completion-box h2 {
                color: white !important;
                margin: 0 0 12px 0;
            }
            .completion-box p {
                color: rgba(255,255,255,0.9) !important;
                margin: 0;
                font-size: 16px;
            }
            </style>
            <div class="completion-box">
                <h2>🎉 튜토리얼 완료!</h2>
                <p>이제 AutoArticle의 모든 기능을 자유롭게 사용해보세요.</p>
            </div>
        """, unsafe_allow_html=True)
        return
    
    # 현재 단계 정보
    if step < 1 or step > TOTAL_STEPS:
        return
    
    content = TOUR_CONTENT[step]
    progress_pct = int((step / TOTAL_STEPS) * 100)
    
    # 안내 패널 CSS + HTML
    st.markdown(f"""
        <style>
        .guide-panel {{
            background: linear-gradient(135deg, #FF8C42 0%, #FF6B1A 100%);
            color: white;
            padding: 20px 24px;
            border-radius: 16px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(255, 140, 66, 0.3);
        }}
        .guide-panel h3 {{
            color: white !important;
            margin: 0 0 8px 0;
            font-size: 18px;
        }}
        .guide-panel p {{
            color: rgba(255,255,255,0.95) !important;
            margin: 0;
            font-size: 15px;
            line-height: 1.5;
        }}
        .progress-bar {{
            background: rgba(255,255,255,0.3);
            border-radius: 10px;
            height: 8px;
            margin-top: 16px;
            overflow: hidden;
        }}
        .progress-fill {{
            background: white;
            height: 100%;
            width: {progress_pct}%;
            border-radius: 10px;
            transition: width 0.3s ease;
        }}
        </style>
        <div class="guide-panel">
            <h3>{content['title']}</h3>
            <p>{content['desc']}</p>
            <div class="progress-bar">
                <div class="progress-fill"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def get_highlight_css():
    """현재 단계에 맞는 강조 CSS 반환"""
    if not is_demo_active() or is_tour_complete():
        return ""
    
    step = get_current_step()
    
    # 각 단계별 타겟 요소에 적용할 CSS
    css_rules = {
        1: """
            /* API Key 입력란 강조 */
            [data-testid="stSidebar"] .stTextInput:first-of-type > div > div {
                border: 3px solid #FF8C42 !important;
                box-shadow: 0 0 20px rgba(255, 140, 66, 0.5) !important;
                animation: pulse 2s infinite;
            }
        """,
        2: """
            /* 행사 정보 폼 강조 - 메인 영역 */
            .main .stTextInput > div > div,
            .main .stTextArea > div > div,
            .main .stSelectbox > div > div,
            .main .stDateInput > div > div {
                border: 2px solid #FF8C42 !important;
                box-shadow: 0 0 10px rgba(255, 140, 66, 0.3) !important;
            }
        """,
        3: """
            /* 생성 버튼 강조 */
            .main .stButton > button[kind="primary"] {
                animation: pulse 1.5s infinite !important;
                box-shadow: 0 0 30px rgba(255, 140, 66, 0.6) !important;
            }
        """,
        4: """
            /* 기사 목록 테이블 강조 */
            .main .stDataFrame,
            .main table {
                border: 3px solid #FF8C42 !important;
                box-shadow: 0 0 20px rgba(255, 140, 66, 0.4) !important;
                border-radius: 12px;
            }
        """,
        5: """
            /* 뉴스레터 생성 버튼 강조 */
            .main .stButton > button[kind="primary"] {
                animation: pulse 1.5s infinite !important;
                box-shadow: 0 0 30px rgba(255, 140, 66, 0.6) !important;
            }
        """
    }
    
    base_css = """
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.02); }
        }
    """
    
    return base_css + css_rules.get(step, "")


def inject_tour_css():
    """투어 관련 CSS 주입"""
    if not is_demo_active():
        return
    
    css = get_highlight_css()
    if css:
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def get_required_menu():
    """현재 단계에 필요한 메뉴 반환 (자동 네비게이션용)"""
    step = get_current_step()
    if step in [1, 2, 3]:
        return "📝 기사 작성"
    elif step in [4, 5]:
        return "🗂️ 보관함 및 뉴스레터"
    return None
