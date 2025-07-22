import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '00_공통설정'))

import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
from aws_multi_account_monitor import AWSMultiAccountMonitor
import time

# 페이지 설정
st.set_page_config(
    page_title="AWS Multi-Account Health Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 사용자 정의 CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF9500 0%, #FF6B35 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .account-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #FF9500;
        margin-bottom: 1rem;
    }
    
    .healthy { border-left-color: #28a745; }
    .warning { border-left-color: #ffc107; }
    .critical { border-left-color: #dc3545; }
    .error { border-left-color: #6c757d; }
    
    .metric-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 0.5rem 0;
    }
    
    .status-badge {
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        color: white;
        font-weight: bold;
        font-size: 0.8rem;
    }
    
    .badge-healthy { background-color: #28a745; }
    .badge-warning { background-color: #ffc107; }
    .badge-critical { background-color: #dc3545; }
    .badge-error { background-color: #6c757d; }
</style>
""", unsafe_allow_html=True)

# 메인 헤더
st.markdown("""
<div class="main-header">
    <h1>🔍 AWS Multi-Account Health Dashboard</h1>
    <p>여러 AWS 계정의 Health 상태를 한번에 모니터링</p>
</div>
""", unsafe_allow_html=True)

# 사이드바 설정
with st.sidebar:
    st.markdown("### ⚙️ 설정")
    
    # 자동 새로고침 설정
    auto_refresh = st.checkbox("자동 새로고침 (60초)", value=False)
    
    # 조회 기간 설정
    days_back = st.selectbox(
        "조회 기간",
        options=[1, 3, 7, 14, 30],
        index=2,
        format_func=lambda x: f"최근 {x}일"
    )
    
    # 보기 옵션
    st.markdown("### 👁️ 보기 옵션")
    show_healthy = st.checkbox("정상 계정 표시", value=True)
    show_warning = st.checkbox("경고 계정 표시", value=True)
    show_critical = st.checkbox("중요 계정 표시", value=True)
    show_error = st.checkbox("오류 계정 표시", value=True)
    
    # 상세 정보 표시
    show_details = st.checkbox("상세 정보 표시", value=False)
    
    # 수동 새로고침
    if st.button("🔄 전체 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    # 마지막 업데이트 시간
    st.markdown("### ⏰ 마지막 업데이트")
    st.text(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# 멀티 계정 데이터 로딩
@st.cache_data(ttl=300)  # 5분 캐시
def get_multi_account_data(days_back):
    monitor = AWSMultiAccountMonitor()
    all_accounts_data = monitor.get_all_accounts_health(days_back)
    consolidated_report = monitor.generate_consolidated_report(all_accounts_data)
    return {
        'all_accounts_data': all_accounts_data,
        'consolidated_report': consolidated_report
    }

# 데이터 로딩
try:
    with st.spinner("모든 AWS 계정의 Health 데이터를 불러오는 중..."):
        data = get_multi_account_data(days_back)
        all_accounts_data = data['all_accounts_data']
        consolidated_report = data['consolidated_report']
    
    if not all_accounts_data:
        st.error("설정된 AWS 계정이 없습니다. aws_config.json 파일을 확인하세요.")
        st.stop()
    
    # 전체 요약 대시보드
    st.subheader("📊 전체 요약")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("총 계정", consolidated_report['total_accounts'])
    
    with col2:
        st.metric("정상 계정", consolidated_report['healthy_accounts'], 
                 delta=None if consolidated_report['healthy_accounts'] == consolidated_report['total_accounts'] else "")
    
    with col3:
        st.metric("경고 계정", consolidated_report['warning_accounts'],
                 delta=f"-{consolidated_report['warning_accounts']}" if consolidated_report['warning_accounts'] > 0 else None)
    
    with col4:
        st.metric("중요 계정", consolidated_report['critical_accounts'],
                 delta=f"-{consolidated_report['critical_accounts']}" if consolidated_report['critical_accounts'] > 0 else None)
    
    with col5:
        st.metric("오류 계정", consolidated_report['error_accounts'],
                 delta=f"-{consolidated_report['error_accounts']}" if consolidated_report['error_accounts'] > 0 else None)
    
    # 전체 상태 표시
    overall_status = consolidated_report['overall_status']
    if overall_status == 'HEALTHY':
        st.success("✅ 모든 계정이 정상 상태입니다!")
    elif overall_status == 'WARNING':
        st.warning("⚠️ 일부 계정에 주의가 필요한 이벤트가 있습니다.")
    else:
        st.error("🚨 중요한 이슈가 감지되었습니다. 즉시 확인이 필요합니다!")
    
    # 계정별 상태 카드
    st.subheader("🏢 계정별 상태")
    
    # 필터링된 계정 목록
    filtered_accounts = []
    for account_summary in consolidated_report['account_summary']:
        status = account_summary['status']
        if ((status == 'HEALTHY' and show_healthy) or 
            (status == 'WARNING' and show_warning) or
            (status == 'CRITICAL' and show_critical) or
            (status == 'ERROR' and show_error)):
            filtered_accounts.append(account_summary)
    
    # 계정 카드 표시
    for account in filtered_accounts:
        status = account['status'].lower()
        status_colors = {
            'healthy': 'success',
            'warning': 'warning', 
            'critical': 'error',
            'error': 'secondary'
        }
        
        with st.container():
            st.markdown(f"""
            <div class="account-card {status}">
                <div class="metric-row">
                    <h3>{account['account']}</h3>
                    <span class="status-badge badge-{status}">{account['status']}</span>
                </div>
            """, unsafe_allow_html=True)
            
            if account['status'] != 'ERROR':
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("중요 이슈", account['critical_events'])
                with col2:
                    st.metric("활성 이벤트", account['active_events'])
                with col3:
                    st.metric("총 이벤트", account['total_events'])
                with col4:
                    st.metric("영향받은 서비스", account['services_affected'])
                
                # 상세 정보 표시
                if show_details and account['account'] in all_accounts_data:
                    account_data = all_accounts_data[account['account']]
                    
                    with st.expander(f"📋 {account['account']} 상세 정보"):
                        # 최근 이벤트 목록
                        events = account_data.get('events', [])
                        if events:
                            st.write("**최근 이벤트:**")
                            events_df = pd.DataFrame(events[:5])  # 최대 5개만 표시
                            st.dataframe(events_df[['service', 'event_type_category', 'region', 'status']], 
                                       use_container_width=True)
                        else:
                            st.write("최근 이벤트가 없습니다.")
            else:
                st.error(f"오류: {account.get('error', 'Unknown error')}")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # 통계 차트
    if len(consolidated_report['account_summary']) > 1:
        st.subheader("📈 통계 차트")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 계정 상태 분포
            status_counts = {
                'HEALTHY': consolidated_report['healthy_accounts'],
                'WARNING': consolidated_report['warning_accounts'], 
                'CRITICAL': consolidated_report['critical_accounts'],
                'ERROR': consolidated_report['error_accounts']
            }
            
            # 0인 항목 제거
            status_counts = {k: v for k, v in status_counts.items() if v > 0}
            
            if status_counts:
                fig_status = px.pie(
                    values=list(status_counts.values()),
                    names=list(status_counts.keys()),
                    title="계정 상태 분포",
                    color_discrete_map={
                        'HEALTHY': '#28a745',
                        'WARNING': '#ffc107',
                        'CRITICAL': '#dc3545',
                        'ERROR': '#6c757d'
                    }
                )
                st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            # 계정별 이벤트 수
            account_events = []
            for account in consolidated_report['account_summary']:
                if account['status'] != 'ERROR':
                    account_events.append({
                        'account': account['account'],
                        'critical': account['critical_events'],
                        'active': account['active_events']
                    })
            
            if account_events:
                events_df = pd.DataFrame(account_events)
                fig_events = px.bar(
                    events_df,
                    x='account',
                    y=['critical', 'active'],
                    title="계정별 이벤트 수",
                    color_discrete_map={
                        'critical': '#dc3545',
                        'active': '#ffc107'
                    }
                )
                fig_events.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_events, use_container_width=True)
    
    # 자동 새로고침
    if auto_refresh:
        time.sleep(60)
        st.rerun()

except Exception as e:
    st.error(f"멀티 계정 데이터 로딩 중 오류가 발생했습니다: {str(e)}")
    st.markdown("""
    ### 🔧 문제 해결 방법:
    1. **설정 파일 확인**: `aws_config.json` 파일이 올바르게 설정되었는지 확인
    2. **AWS 자격 증명 확인**: 각 계정의 액세스 키가 유효한지 확인  
    3. **권한 확인**: Health API 사용을 위한 권한이 있는지 확인
    4. **지원 플랜 확인**: Business/Enterprise 지원 플랜이 필요
    """)

# 푸터
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🔍 AWS Multi-Account Health Dashboard | 통합 모니터링 솔루션</p>
    <p><small>마지막 업데이트: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</small></p>
</div>
""", unsafe_allow_html=True)