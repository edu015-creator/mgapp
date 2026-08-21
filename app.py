import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="업무 지원 요청 현황 대시보드", page_icon="📋", layout="wide")

st.title("📋 업무 지원 요청 데이터 시각화")
st.markdown("업무지원요청 CSV 파일을 업로드하면 **요청 현황, 긴급도, 처리 상태 및 AI 처리 가능 여부**를 자동으로 분석해 드립니다.")

# 파일 업로더
uploaded_file = st.file_uploader("📂 CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file is not None:
    # 한글 인코딩 대응
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(uploaded_file, encoding='cp949')

    st.success("✅ 파일 업로드 완료!")
    
    # 1. 핵심 지표 (KPI Metrics)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("총 요청 건수", f"{len(df)}건")
    with col2:
        completed = len(df[df['status'] == '완료']) if 'status' in df.columns else 0
        st.metric("완료된 건수", f"{completed}건")
    with col3:
        urgent = len(df[df['urgency'] == '상']) if 'urgency' in df.columns else 0
        st.metric("긴급('상') 건수", f"{urgent}건")
    with col4:
        ai_ready = len(df[df['ai_handling'] == '전용AI가능']) if 'ai_handling' in df.columns else 0
        st.metric("전용 AI 대응 가능", f"{ai_ready}건")

    st.markdown("---")

    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["📊 차트 대시보드", "🔍 데이터 필터링 & 상세보기", "📋 전체 데이터"])

    # -------------------------------------------------------------
    # TAB 1: 주요 차트 대시보드
    # -------------------------------------------------------------
    with tab1:
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("📌 카테고리별 요청 건수")
            if 'category' in df.columns:
                cat_counts = df['category'].value_counts().reset_index()
                cat_counts.columns = ['category', 'count']
                fig_cat = px.bar(
                    cat_counts, x='category', y='count',
                    labels={'category': '카테고리', 'count': '건수'},
                    color='category', text='count'
                )
                st.plotly_chart(fig_cat, use_container_width=True)

        with c2:
            st.subheader("🚨 긴급도별 상태 분포")
            if 'urgency' in df.columns and 'status' in df.columns:
                fig_urgency = px.histogram(
                    df, x='urgency', color='status', barmode='group',
                    labels={'urgency': '긴급도', 'status': '처리 상태', 'count': '건수'}
                )
                st.plotly_chart(fig_urgency, use_container_width=True)

        c3, c4 = st.columns(2)

        with c3:
            st.subheader("🤖 AI 처리 가능 여부 비중")
            if 'ai_handling' in df.columns:
                fig_ai = px.pie(
                    df, names='ai_handling', hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(fig_ai, use_container_width=True)

        with c4:
            st.subheader("📅 일자별 요청 추세")
            if 'request_date' in df.columns:
                date_df = df.groupby('request_date').size().reset_index(name='count')
                fig_date = px.line(
                    date_df, x='request_date', y='count', markers=True,
                    labels={'request_date': '요청 일자', 'count': '건수'}
                )
                st.plotly_chart(fig_date, use_container_width=True)

    # -------------------------------------------------------------
    # TAB 2: 데이터 필터링
    # -------------------------------------------------------------
    with tab2:
        st.subheader("🔍 조건별 요청 데이터 검색")
        
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            selected_cat = st.multiselect("카테고리 선택", df['category'].unique() if 'category' in df.columns else [], default=df['category'].unique() if 'category' in df.columns else [])
        with f_col2:
            selected_urgency = st.multiselect("긴급도 선택", df['urgency'].unique() if 'urgency' in df.columns else [], default=df['urgency'].unique() if 'urgency' in df.columns else [])
        with f_col3:
            selected_status = st.multiselect("처리 상태 선택", df['status'].unique() if 'status' in df.columns else [], default=df['status'].unique() if 'status' in df.columns else [])

        # 필터링 적용
        filtered_df = df[
            (df['category'].isin(selected_cat)) &
            (df['urgency'].isin(selected_urgency)) &
            (df['status'].isin(selected_status))
        ]

        st.write(f"검색 결과: 총 **{len(filtered_df)}** 건")
        st.dataframe(filtered_df, use_container_width=True)

    # -------------------------------------------------------------
    # TAB 3: 전체 데이터 및 다운로드
    # -------------------------------------------------------------
    with tab3:
        st.subheader("📋 전체 파일 데이터")
        st.dataframe(df, use_container_width=True)
        
        csv_bytes = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 CSV 파일 다운로드",
            data=csv_bytes,
            file_name="processed_requests.csv",
            mime="text/csv"
        )
else:
    st.info("👆 상단의 [CSV 파일] 업로드 영역에 `업무지원요청_합성자료 (1).csv` 파일을 드래그앤드롭해 주세요.")
