"""
Demo Tour Module - Enhanced with Banner Guides & Visual Highlights
Provides interactive tour functionality with on-screen guidance.
"""
import streamlit as st

# Demo tour에서 사용할 샘플 기사 데이터
DEMO_ARTICLE_SAMPLE = {
    "grade": "3학년",
    "event_name": "찾아가는 목공 체험",
    "location": "강당",
    "tone": "따뜻하고 감성적인",
    "keywords": "나무 냄새, 망치질 소리, 목공 체험, 아이들의 집중하는 모습"
}


def init_demo_mode():
    """데모 모드 상태 초기화"""
    if "demo_mode" not in st.session_state:
        st.session_state.demo_mode = False
    if "demo_step" not in st.session_state:
        st.session_state.demo_step = 0
    if "demo_data_loaded" not in st.session_state:
        st.session_state.demo_data_loaded = False


def start_demo():
    """데모 시작: 데이터 로드 및 투어 시작"""
    from demo_data import load_demo_data_to_db
    from engines.db_service import DatabaseService
    
    st.session_state.demo_mode = True
    st.session_state.demo_step = 1  # 1: Welcome
    st.session_state.demo_data_loaded = True
    
    # 데모 데이터 로드
    load_demo_data_to_db(DatabaseService())


def exit_demo():
    """데모 종료 및 데이터 정리"""
    from demo_data import clear_demo_data_from_db
    from engines.db_service import DatabaseService
    
    st.session_state.demo_mode = False
    st.session_state.demo_step = 0
    st.session_state.demo_data_loaded = False
    
    clear_demo_data_from_db(DatabaseService())


def next_step():
    """다음 단계로 이동"""
    st.session_state.demo_step += 1


def prev_step():
    """이전 단계로 이동"""
    if st.session_state.demo_step > 1:
        st.session_state.demo_step -= 1


def get_demo_step():
    """현재 데모 단계 반환"""
    return st.session_state.get("demo_step", 0)


def is_demo_active():
    """데모 모드 활성화 여부"""
    return st.session_state.get("demo_mode", False)


def inject_highlight_css():
    """데모용 CSS 스타일 주입 (하이라이트, 애니메이션)"""
    st.markdown("""
        <style>
        /* 데모 가이드 배너 */
        .demo-banner {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 24px;
            border-radius: 16px;
            margin-bottom: 24px;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
            animation: fadeSlideIn 0.5s ease-out;
        }
        .demo-banner h3 {
            margin: 0 0 8px 0;
            font-size: 1.3rem;
            color: white !important;
        }
        .demo-banner p {
            margin: 0;
            opacity: 0.95;
            line-height: 1.6;
            color: white !important;
        }
        .demo-banner-action {
            background: rgba(255,255,255,0.2);
            border-radius: 12px;
            padding: 12px 16px;
            margin-top: 16px;
            font-weight: 600;
            border-left: 4px solid #FFD700;
        }
        
        /* 진행 상황 표시 */
        .demo-progress {
            display: flex;
            gap: 8px;
            margin-top: 16px;
        }
        .demo-progress-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: rgba(255,255,255,0.3);
        }
        .demo-progress-dot.active {
            background: #FFD700;
            box-shadow: 0 0 8px rgba(255, 215, 0, 0.6);
        }
        .demo-progress-dot.completed {
            background: #90EE90;
        }
        
        /* 하이라이트 효과 (Glow) */
        .demo-highlight-area {
            position: relative;
            border: 3px solid #FF6B6B !important;
            border-radius: 16px !important;
            box-shadow: 0 0 20px rgba(255, 107, 107, 0.4), 
                        0 0 40px rgba(255, 107, 107, 0.2) !important;
            animation: pulseGlow 2s infinite;
        }
        @keyframes pulseGlow {
            0%, 100% { box-shadow: 0 0 20px rgba(255, 107, 107, 0.4); }
            50% { box-shadow: 0 0 30px rgba(255, 107, 107, 0.6), 0 0 60px rgba(255, 107, 107, 0.3); }
        }
        
        /* 포인터 화살표 */
        .demo-pointer {
            font-size: 24px;
            animation: bounce 1s infinite;
        }
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-8px); }
        }
        
        /* 애니메이션 */
        @keyframes fadeSlideIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* 성공 배너 */
        .demo-success-banner {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            padding: 24px;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 24px;
        }
        </style>
    """, unsafe_allow_html=True)


def render_sidebar_demo_button():
    """사이드바에 데모 버튼 렌더링"""
    init_demo_mode()
    
    if not is_demo_active():
        st.markdown("""
            <div style="background: linear-gradient(135deg, #FF8C42 0%, #FF6B1A 100%); 
                        border-radius: 16px; padding: 16px; margin-bottom: 20px; text-align: center;">
                <div style="color: white; font-size: 14px; font-weight: 500;">🌟 처음이신가요?</div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("✨ 30초 체험하기", key="start_demo_btn", use_container_width=True, type="primary"):
            start_demo()
            st.rerun()
    else:
        st.markdown("""
            <div style="background: #E8F5E9; border-radius: 12px; padding: 12px; text-align: center; margin-bottom: 16px;">
                <span style="color: #2E7D32; font-weight: 600;">🎯 체험 모드 진행 중</span>
            </div>
        """, unsafe_allow_html=True)
        
        step = get_demo_step()
        st.caption(f"현재 단계: {step} / 5")
        
        if st.button("🚪 체험 종료", key="exit_demo_btn", use_container_width=True):
            exit_demo()
            st.rerun()


def render_demo_guide_banner():
    """
    현재 데모 단계에 맞는 가이드 배너를 메인 화면 상단에 렌더링합니다.
    이 함수는 ui_logic.py의 각 render 함수 시작 부분에서 호출됩니다.
    """
    if not is_demo_active():
        return
    
    inject_highlight_css()
    step = get_demo_step()
    total_steps = 5
    
    # 진행 상황 점(dots) HTML 생성
    dots_html = ""
    for i in range(1, total_steps + 1):
        if i < step:
            dots_html += '<div class="demo-progress-dot completed"></div>'
        elif i == step:
            dots_html += '<div class="demo-progress-dot active"></div>'
        else:
            dots_html += '<div class="demo-progress-dot"></div>'
    
    # 단계별 가이드 콘텐츠
    guide_content = {
        1: {
            "title": "👋 안녕하세요! AI 학교 소식 작성 도구입니다",
            "desc": "30초 만에 AI가 어떻게 기사를 작성하는지 보여드릴게요.<br>먼저 <b>보관함에서 완성된 기사</b>들을 살펴볼까요?",
            "action": "👈 왼쪽 사이드바에서 <b>'🗂️ 보관함 및 뉴스레터'</b>를 클릭하세요!"
        },
        2: {
            "title": "📋 기사 보관함 둘러보기",
            "desc": "저장된 기사 목록이 보이시나요? AI가 작성한 다양한 학교 소식들이 있습니다.",
            "action": "👇 아래 <b>'기사 상세 조회 및 수정'</b>을 펼쳐서 기사 하나를 선택해보세요!"
        },
        3: {
            "title": "📰 뉴스레터 만들기 체험",
            "desc": "여러 기사를 선택해서 PDF, Word, PPT 문서를 한 번에 만들 수 있어요!",
            "action": "👇 기사를 2개 이상 선택하고 <b>'통합 문서 생성'</b> 버튼을 눌러보세요!"
        },
        4: {
            "title": "✍️ 새 기사 작성하기",
            "desc": "이제 직접 새 기사를 작성해볼까요? AI가 행사 정보를 기반으로 기사를 자동 생성합니다.",
            "action": "👈 사이드바에서 <b>'📝 기사 작성'</b>을 클릭하고, 양식을 채워보세요!"
        },
        5: {
            "title": "🎉 체험 완료!",
            "desc": "축하드려요! AI 학교 소식 도구의 핵심 기능을 모두 체험하셨습니다.<br>" +
                   "• 기사 보관함 조회 ✅<br>• 뉴스레터(PDF/Word/PPT) 생성 ✅<br>• AI 기사 작성 ✅",
            "action": "이제 <b>직접 사용해보세요!</b> 데모 종료 후 실제 기사를 작성할 수 있습니다."
        }
    }
    
    if step not in guide_content:
        return
    
    content = guide_content[step]
    
    # 배너 HTML 렌더링
    if step == 5:
        # 완료 화면은 성공 배너로
        st.markdown(f"""
            <div class="demo-success-banner">
                <h2 style="margin:0 0 12px 0; color:white !important;">{content['title']}</h2>
                <p style="margin:0; color:white !important; opacity:0.95;">{content['desc']}</p>
                <div style="margin-top:16px; padding:12px; background:rgba(255,255,255,0.2); border-radius:12px;">
                    <span style="color:white !important;">{content['action']}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🏠 홈으로 돌아가기 (데모 종료)", type="primary", use_container_width=True):
            exit_demo()
            st.rerun()
    else:
        st.markdown(f"""
            <div class="demo-banner">
                <h3>{content['title']}</h3>
                <p>{content['desc']}</p>
                <div class="demo-banner-action">
                    <span class="demo-pointer">👉</span> {content['action']}
                </div>
                <div class="demo-progress">
                    {dots_html}
                    <span style="margin-left: 8px; font-size: 12px;">Step {step}/{total_steps}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # 네비게이션 버튼
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if step > 1:
                if st.button("← 이전", key="demo_prev"):
                    prev_step()
                    st.rerun()
        with col2:
            if st.button("건너뛰기", key="demo_skip"):
                st.session_state.demo_step = 5
                st.rerun()
        with col3:
            if st.button("다음 →", key="demo_next", type="primary"):
                next_step()
                st.rerun()


def should_highlight_area(area_name: str) -> bool:
    """
    특정 영역이 현재 단계에서 하이라이트되어야 하는지 확인합니다.
    area_name: 'archive_list', 'article_detail', 'newsletter_action', 'write_form' 등
    """
    if not is_demo_active():
        return False
    
    step = get_demo_step()
    
    highlight_map = {
        1: ["menu_radio"],  # 메뉴 선택
        2: ["archive_list", "article_detail"],  # 기사 목록, 상세 보기
        3: ["newsletter_action"],  # 뉴스레터 생성 버튼
        4: ["write_form"],  # 기사 작성 폼
    }
    
    return area_name in highlight_map.get(step, [])


def get_highlight_container(area_name: str):
    """
    하이라이트가 필요한 영역을 위한 컨테이너 스타일 반환.
    사용 예: with st.container(border=should_highlight_area('write_form')):
    """
    if should_highlight_area(area_name):
        return True
    return False
