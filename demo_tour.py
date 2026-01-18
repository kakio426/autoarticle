"""
Demo Tour Module
Provides interactive tour functionality for the app.
"""
import streamlit as st

# Tour step definitions - 12 steps covering all features
TOUR_STEPS = [
    {
        "id": 1,
        "title": "🔑 API 키 입력",
        "description": "Gemini API 키를 입력해야 AI 기능을 사용할 수 있습니다.\n\n'API 키 발급 방법'을 클릭하면 상세 안내를 볼 수 있어요!",
        "target": "sidebar",
        "action": "👈 왼쪽 사이드바의 'Gemini API Key' 입력창을 확인하세요.",
        "area": "sidebar"
    },
    {
        "id": 2,
        "title": "🏫 학교명 설정",
        "description": "여기에 학교 이름을 입력하면 생성되는 모든 문서에 자동으로 적용됩니다.",
        "target": "sidebar",
        "action": "👈 학교명을 원하는 이름으로 변경해보세요.",
        "area": "sidebar"
    },
    {
        "id": 3,
        "title": "🎨 디자인 테마 선택",
        "description": "테마를 선택하면 PDF, Word, 카드뉴스의 색상이 모두 변경됩니다.\n\n오렌지, 블루, 그린 등 다양한 색상을 지원해요!",
        "target": "sidebar",
        "action": "👈 테마 목록에서 다른 색상을 선택해보세요.",
        "area": "sidebar"
    },
    {
        "id": 4,
        "title": "📂 메뉴 전환",
        "description": "두 가지 주요 모드가 있습니다:\n\n• **기사 작성**: 새로운 학교 소식 작성\n• **보관함 및 뉴스레터**: 저장된 기사 관리 및 발행",
        "target": "sidebar",
        "action": "👈 '기사 작성' 또는 '보관함 및 뉴스레터'를 선택해보세요.",
        "area": "sidebar"
    },
    {
        "id": 5,
        "title": "📝 행사 정보 입력",
        "description": "기사를 작성하려면 먼저 행사 정보를 입력합니다.\n\n• 참여 학년\n• 행사명\n• 장소와 일시\n• 기사 톤(분위기)\n• 주요 활동 내용",
        "target": "write_form",
        "action": "👉 오른쪽 폼에서 각 항목을 채워보세요.",
        "area": "write_mode"
    },
    {
        "id": 6,
        "title": "📸 사진 업로드",
        "description": "행사 사진을 업로드하면 기사와 함께 표시됩니다.\n\n여러 장을 한 번에 올리고, 원하는 사진만 선택할 수 있어요!",
        "target": "photo_upload",
        "action": "👉 '사진 관리' 섹션에서 사진을 업로드해보세요.",
        "area": "write_mode"
    },
    {
        "id": 7,
        "title": "✨ AI 초안 생성",
        "description": "모든 정보를 입력한 후 버튼을 클릭하면 Gemini AI가 자동으로 기사를 작성합니다!\n\n약 5-10초 정도 소요됩니다.",
        "target": "generate_button",
        "action": "👉 '기사 초안 생성하기' 버튼을 클릭해보세요.",
        "area": "write_mode"
    },
    {
        "id": 8,
        "title": "✏️ 기사 편집",
        "description": "AI가 생성한 초안을 자유롭게 수정할 수 있습니다.\n\n• 제목 수정\n• 본문 수정\n• 해시태그 편집",
        "target": "edit_section",
        "action": "👉 AI가 작성한 기사를 원하는 대로 수정해보세요.",
        "area": "write_mode"
    },
    {
        "id": 9,
        "title": "🖼️ 카드뉴스 즉시 제작",
        "description": "작성한 기사를 SNS용 카드뉴스 이미지로 바로 변환합니다!\n\nPNG 파일로 다운로드할 수 있어요.",
        "target": "card_button",
        "action": "👉 '카드뉴스 즉시 제작' 버튼을 찾아보세요.",
        "area": "write_mode"
    },
    {
        "id": 10,
        "title": "📋 기사 보관함",
        "description": "저장된 모든 기사가 여기에 표시됩니다.\n\n날짜, 행사명, 학년, 톤 정보를 한눈에 볼 수 있어요!",
        "target": "archive_list",
        "action": "👉 왼쪽 메뉴에서 '보관함 및 뉴스레터'를 선택하면 목록이 나타납니다.",
        "area": "publish_mode"
    },
    {
        "id": 11,
        "title": "📰 뉴스레터 생성",
        "description": "여러 기사를 선택해서 한 번에 문서로 만들 수 있습니다!\n\n• **PDF**: 인쇄용 고품질 문서\n• **Word**: 편집 가능한 문서\n• **PPT**: 발표용 슬라이드",
        "target": "newsletter_section",
        "action": "👉 기사를 선택하고 '통합 문서 생성' 버튼을 클릭해보세요.",
        "area": "publish_mode"
    },
    {
        "id": 12,
        "title": "🔍 기사 상세 및 수정",
        "description": "저장된 기사를 언제든 다시 확인하고 수정할 수 있습니다.\n\n개별 기사로 카드뉴스를 만들 수도 있어요!",
        "target": "detail_view",
        "action": "👉 '기사 상세 조회 및 수정'을 펼쳐서 확인해보세요.",
        "area": "publish_mode"
    }
]


def init_tour_state():
    """Initialize tour-related session state variables."""
    if 'demo_mode' not in st.session_state:
        st.session_state.demo_mode = False
    if 'tour_active' not in st.session_state:
        st.session_state.tour_active = False
    if 'tour_step' not in st.session_state:
        st.session_state.tour_step = 0


def render_demo_button():
    """
    Render the 'Try Demo' button in the sidebar.
    Returns True if demo mode should be activated.
    """
    init_tour_state()
    
    if not st.session_state.demo_mode:
        st.markdown("""
            <style>
            .demo-button-container {
                background: linear-gradient(135deg, #FF8C42 0%, #FF6B1A 100%);
                border-radius: 16px;
                padding: 16px;
                margin-bottom: 20px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(255, 140, 66, 0.3);
            }
            .demo-button-title {
                color: white;
                font-size: 14px;
                margin-bottom: 8px;
                font-weight: 500;
            }
            </style>
            <div class="demo-button-container">
                <div class="demo-button-title">처음이신가요?</div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎯 기능 체험해보기", key="demo_btn", use_container_width=True):
            return True
    else:
        # Show tour control if demo mode is active
        st.markdown("""
            <div style="background: #E8F5E9; border-radius: 12px; padding: 12px; margin-bottom: 16px; text-align: center;">
                <span style="color: #2E7D32; font-weight: 600;">✅ 체험 모드 활성화됨</span>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 투어 재시작", key="restart_tour", use_container_width=True):
                st.session_state.tour_active = True
                st.session_state.tour_step = 0
                st.rerun()
        with col2:
            if st.button("🚪 체험 종료", key="end_demo", use_container_width=True):
                st.session_state.demo_mode = False
                st.session_state.tour_active = False
                st.session_state.tour_step = 0
                # Clear demo data
                from demo_data import clear_demo_data_from_db
                from engines.db_service import DatabaseService
                clear_demo_data_from_db(DatabaseService())
                st.rerun()
    
    return False


def start_demo_mode():
    """Activate demo mode and load demo data."""
    from demo_data import load_demo_data_to_db
    from engines.db_service import DatabaseService
    
    st.session_state.demo_mode = True
    st.session_state.tour_active = True
    st.session_state.tour_step = 0
    
    # Load demo data
    load_demo_data_to_db(DatabaseService())


def render_tour_overlay():
    """Render the tour overlay if tour is active."""
    if not st.session_state.get('tour_active', False):
        return
    
    current_step = st.session_state.get('tour_step', 0)
    if current_step < 0 or current_step >= len(TOUR_STEPS):
        st.session_state.tour_active = False
        return
    
    step = TOUR_STEPS[current_step]
    total_steps = len(TOUR_STEPS)
    progress_percent = ((current_step + 1) / total_steps) * 100
    
    # Add custom CSS for the tour container
    st.markdown("""
        <style>
        .tour-container {
            background: white;
            border: 3px solid #FF8C42;
            border-radius: 20px;
            padding: 24px;
            margin: 20px 0;
            box-shadow: 0 10px 40px rgba(255, 140, 66, 0.2);
        }
        .tour-step-badge {
            display: inline-block;
            background: linear-gradient(135deg, #FF8C42, #FF6B1A);
            color: white;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 12px;
        }
        .tour-progress-track {
            width: 100%;
            height: 6px;
            background: #EEE;
            border-radius: 3px;
            margin-bottom: 16px;
            overflow: hidden;
        }
        .tour-progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #FF8C42, #FF6B1A);
            border-radius: 3px;
            transition: width 0.4s ease;
        }
        .tour-title-text {
            font-size: 22px;
            font-weight: 700;
            color: #333;
            margin-bottom: 12px;
        }
        .tour-desc-text {
            font-size: 15px;
            line-height: 1.7;
            color: #555;
            margin-bottom: 16px;
        }
        .tour-action-box {
            background: linear-gradient(135deg, #FFF8E1, #FFECB3);
            border: 2px solid #FFE082;
            border-radius: 12px;
            padding: 14px 18px;
            font-size: 15px;
            color: #E65100;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Create the tour content with Streamlit native elements
    with st.container(border=True):
        # Header with step indicator
        st.markdown(f'<div class="tour-step-badge">🎯 Step {current_step + 1} / {total_steps}</div>', unsafe_allow_html=True)
        
        # Progress bar
        st.markdown(f'''
            <div class="tour-progress-track">
                <div class="tour-progress-fill" style="width: {progress_percent}%;"></div>
            </div>
        ''', unsafe_allow_html=True)
        
        # Title
        st.markdown(f'## {step["title"]}')
        
        # Description - use st.markdown for proper text rendering
        st.markdown(step['description'])
        
        # Action hint
        st.markdown(f'<div class="tour-action-box">{step["action"]}</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Navigation buttons in columns
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if current_step > 0:
                if st.button("← 이전", key="tour_prev", use_container_width=True):
                    st.session_state.tour_step -= 1
                    st.rerun()
        
        with col2:
            if st.button("✕ 투어 닫기", key="tour_close", use_container_width=True):
                st.session_state.tour_active = False
                st.rerun()
        
        with col3:
            if current_step < total_steps - 1:
                if st.button("다음 →", key="tour_next", use_container_width=True):
                    st.session_state.tour_step += 1
                    st.rerun()
            else:
                if st.button("🎉 완료!", key="tour_complete", use_container_width=True):
                    st.session_state.tour_active = False
                    st.toast("🎉 투어를 완료했습니다! 이제 자유롭게 사용해보세요.", icon="🎊")
                    st.rerun()


def get_current_tour_area():
    """Get the area that the current tour step is targeting."""
    if not st.session_state.get('tour_active', False):
        return None
    
    current_step = st.session_state.get('tour_step', 0)
    if current_step < 0 or current_step >= len(TOUR_STEPS):
        return None
    
    return TOUR_STEPS[current_step].get('area')
