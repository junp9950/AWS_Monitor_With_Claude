import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '00_공통설정'))

import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
from aws_health_service import AWSHealthService
import time

# 페이지 설정
st.set_page_config(
    page_title="AWS Health Dashboard - 일일 상태 점검",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 사용자 정의 CSS
st.markdown("""
<style>
    /* 메인 컨테이너 스타일 */
    .main-header {
        background: linear-gradient(90deg, #FF9500 0%, #FF6B35 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* 상태 카드 스타일 */
    .status-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #FF9500;
        margin-bottom: 1rem;
    }
    
    .status-good {
        border-left-color: #28a745;
    }
    
    .status-warning {
        border-left-color: #ffc107;
    }
    
    .status-critical {
        border-left-color: #dc3545;
    }
    
    /* 메트릭 카드 */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .metric-number {
        font-size: 2rem;
        font-weight: bold;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* 사이드바 스타일 */
    .sidebar-content {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    /* 알림 스타일 */
    .alert-critical {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .alert-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .alert-info {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 메인 헤더
st.markdown("""
<div class="main-header">
    <h1>🔍 AWS Health Dashboard</h1>
    <p>일일 점검을 위한 AWS 서비스 상태 모니터링</p>
</div>
""", unsafe_allow_html=True)

# 사이드바 설정
with st.sidebar:
    st.markdown("### ⚙️ 설정")
    
    # 임시로 계정 목록 가져오기 (설정 파일 확인용)
    temp_service = AWSHealthService()
    available_accounts = temp_service.get_available_accounts()
    
    # AWS 계정 선택
    if available_accounts:
        selected_account = st.selectbox(
            "AWS 계정 선택",
            options=available_accounts,
            index=0
        )
        st.success(f"선택된 계정: {selected_account}")
    else:
        selected_account = None
        st.warning("AWS 계정 설정이 필요합니다!")
        st.markdown("""
        **설정 방법:**
        1. `aws_config.json.template`을 복사
        2. `aws_config.json` 파일 생성
        3. AWS 계정 정보 입력
        """)
    
    # 자동 새로고침 설정
    auto_refresh = st.checkbox("자동 새로고침 (30초)", value=False)
    
    # 조회 기간 설정
    days_back = st.selectbox(
        "조회 기간",
        options=[1, 3, 7, 14, 30],
        index=2,
        format_func=lambda x: f"최근 {x}일"
    )
    
    # 필터 옵션
    st.markdown("### 🔽 필터")
    show_resolved = st.checkbox("해결된 이벤트 포함", value=False)
    show_scheduled = st.checkbox("예정된 변경사항 포함", value=True)
    
    # 수동 새로고침
    if st.button("🔄 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    # 마지막 업데이트 시간
    st.markdown("### ⏰ 마지막 업데이트")
    st.text(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# AWS Health 서비스 초기화
@st.cache_data(ttl=300)  # 5분 캐시
def get_health_data(days_back, selected_account):
    health_service = AWSHealthService(account_name=selected_account)
    return {
        'summary': health_service.get_health_summary(),
        'events': health_service.get_service_health_events(days_back),
        'services': health_service.get_events_by_service(),
        'regions': health_service.get_events_by_region(),
        'account_events': health_service.check_account_specific_events(),
        'available_accounts': health_service.get_available_accounts(),
        'current_account': health_service.current_account
    }

# 데이터 로딩
try:
    with st.spinner("AWS Health 데이터를 불러오는 중..."):
        health_data = get_health_data(days_back, selected_account)
        
        # 현재 계정 정보 표시
        if health_data.get('current_account'):
            account_info = health_data['current_account']
            st.markdown(f"""
            <div class="alert-info">
                <strong>🔗 연결된 AWS 계정</strong><br>
                계정명: {account_info['name']}<br>
                설명: {account_info['description']}<br>
                리전: {account_info['region']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-warning">
                <strong>⚠️ AWS 계정 설정 필요</strong><br>
                aws_config.json 파일을 생성하고 계정 정보를 입력하세요.
            </div>
            """, unsafe_allow_html=True)
        
    # 요약 정보 표시
    summary = health_data['summary']
    
    # 상단 메트릭 카드
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-number">{summary['total_events']}</p>
            <p class="metric-label">총 이벤트</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);">
            <p class="metric-number">{summary['active_events']}</p>
            <p class="metric-label">활성 이벤트</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);">
            <p class="metric-number">{summary['resolved_events']}</p>
            <p class="metric-label">해결된 이벤트</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%);">
            <p class="metric-number">{summary['critical_events']}</p>
            <p class="metric-label">중요 이슈</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #6f42c1 0%, #e83e8c 100%);">
            <p class="metric-number">{summary['services_affected']}</p>
            <p class="metric-label">영향받은 서비스</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #17a2b8 0%, #6610f2 100%);">
            <p class="metric-number">{summary['regions_affected']}</p>
            <p class="metric-label">영향받은 리전</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 전체 상태 요약
    if summary['active_events'] == 0 and summary['critical_events'] == 0:
        st.markdown("""
        <div class="alert-info">
            <strong>✅ 모든 시스템 정상</strong><br>
            현재 활성 이슈나 중요한 문제가 없습니다.
        </div>
        """, unsafe_allow_html=True)
    elif summary['critical_events'] > 0:
        st.markdown(f"""
        <div class="alert-critical">
            <strong>🚨 중요 이슈 감지</strong><br>
            {summary['critical_events']}개의 중요한 이슈가 진행 중입니다. 즉시 확인이 필요합니다.
        </div>
        """, unsafe_allow_html=True)
    elif summary['active_events'] > 0:
        st.markdown(f"""
        <div class="alert-warning">
            <strong>⚠️ 활성 이벤트 있음</strong><br>
            {summary['active_events']}개의 이벤트가 진행 중입니다.
        </div>
        """, unsafe_allow_html=True)
    
    # 이벤트 목록
    events = health_data['events']
    if events:
        st.subheader("📋 최근 이벤트 목록")
        
        # 이벤트 필터링
        df_events = pd.DataFrame(events)
        
        if not show_resolved:
            df_events = df_events[df_events['end_time'].isnull() | (df_events['end_time'] == '')]
        
        if not show_scheduled:
            df_events = df_events[df_events['event_type_category'] != 'scheduledChange']
        
        # 이벤트 테이블 표시
        if not df_events.empty:
            # 상태별 색상 매핑
            def get_status_color(status):
                if status == 'open':
                    return "🔴"
                elif status == 'closed':
                    return "🟢"
                elif status == 'upcoming':
                    return "🟡"
                else:
                    return "⚪"
            
            # 카테고리별 아이콘 매핑
            def get_category_icon(category):
                if category == 'issue':
                    return "🚨"
                elif category == 'accountNotification':
                    return "📢"
                elif category == 'scheduledChange':
                    return "🔄"
                else:
                    return "📝"
            
            # 표시용 데이터 준비
            display_df = df_events.copy()
            display_df['상태'] = display_df['status'].apply(get_status_color)
            display_df['카테고리'] = display_df['event_type_category'].apply(get_category_icon)
            display_df['서비스'] = display_df['service']
            display_df['리전'] = display_df['region']
            display_df['시작 시간'] = pd.to_datetime(display_df['start_time']).dt.strftime('%Y-%m-%d %H:%M')
            display_df['설명'] = display_df['description'].str[:100] + "..."
            
            st.dataframe(
                display_df[['상태', '카테고리', '서비스', '리전', '시작 시간', '설명']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("필터 조건에 맞는 이벤트가 없습니다.")
    
    # 차트 섹션
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 서비스별 이벤트")
        services_data = health_data['services']
        if services_data:
            services_df = pd.DataFrame.from_dict(services_data, orient='index')
            services_df = services_df.reset_index().rename(columns={'index': 'service'})
            
            fig_services = px.bar(
                services_df,
                x='service',
                y='total_events',
                title="서비스별 이벤트 수",
                color='critical_events',
                color_continuous_scale='Reds'
            )
            fig_services.update_layout(
                xaxis_tickangle=-45,
                height=400
            )
            st.plotly_chart(fig_services, use_container_width=True)
        else:
            st.info("서비스별 데이터가 없습니다.")
    
    with col2:
        st.subheader("🌍 리전별 이벤트")
        regions_data = health_data['regions']
        if regions_data:
            regions_df = pd.DataFrame.from_dict(regions_data, orient='index')
            regions_df = regions_df.reset_index().rename(columns={'index': 'region'})
            
            fig_regions = px.pie(
                regions_df,
                values='total_events',
                names='region',
                title="리전별 이벤트 분포"
            )
            fig_regions.update_layout(height=400)
            st.plotly_chart(fig_regions, use_container_width=True)
        else:
            st.info("리전별 데이터가 없습니다.")
    
    # 계정별 알림
    account_events = health_data['account_events']
    if account_events:
        st.subheader("📬 계정별 알림")
        account_df = pd.DataFrame(account_events)
        
        for _, event in account_df.iterrows():
            with st.expander(f"📢 {event['event_type_code']} - {event['status']}"):
                st.write(f"**서비스:** {event['service']}")
                st.write(f"**리전:** {event['region']}")
                st.write(f"**시작 시간:** {event['start_time']}")
                st.write(f"**설명:** {event['description']}")
    
    # 자동 새로고침
    if auto_refresh:
        time.sleep(30)
        st.rerun()

except Exception as e:
    st.error(f"AWS Health 데이터 로딩 중 오류가 발생했습니다: {str(e)}")
    st.markdown("""
    ### 🔧 문제 해결 방법:
    1. **AWS 자격 증명 확인**: `aws configure` 명령으로 AWS 자격 증명이 올바르게 설정되었는지 확인
    2. **권한 확인**: Health API 사용을 위해 `support:DescribeHealthEvents` 권한이 필요
    3. **리전 확인**: Health API는 `us-east-1` 리전에서만 사용 가능
    4. **Business/Enterprise 지원 플랜**: Health API는 Business 또는 Enterprise 지원 플랜에서만 사용 가능
    """)

# 푸터
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🔍 AWS Health Dashboard | 일일 점검을 위한 통합 모니터링 솔루션</p>
    <p><small>마지막 업데이트: {}</small></p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)