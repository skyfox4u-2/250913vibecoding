import streamlit as st
import pandas as pd
import altair as alt

# 페이지 설정
st.set_page_config(
    page_title="MBTI 유형별 국가 분석 (기본 데이터 활용)",
    page_icon="📊",
    layout="wide"
)

# 제목 및 설명
st.title("📊 MBTI 유형별 국가 TOP 10 분석")
st.markdown("데이터 파일이 존재하면 그 파일을 읽어오고, 없다면 업로드된 파일을 사용합니다.")

# 데이터 로드 함수
@st.cache_data
def load_data(file):
    return pd.read_csv(file)

def get_mbti_proportions(df):
    """국가별 MBTI 유형 비율을 계산하는 함수"""
    if 'country' not in df.columns or 'mbti_type' not in df.columns:
        return None
    
    country_mbti_counts = df.groupby(['country', 'mbti_type']).size().reset_index(name='count')
    total_counts_by_country = df.groupby('country').size().reset_index(name='total')
    
    merged_df = pd.merge(country_mbti_counts, total_counts_by_country, on='country')
    merged_df['proportion'] = merged_df['count'] / merged_df['total']
    
    return merged_df

st.divider()

# 기본 데이터 파일 경로
default_data_path = "mbti_data.csv"

# 1. 파일 업로더
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요 (선택 사항)", type="csv")

df = None
if uploaded_file is not None:
    # 2. 업로드된 파일이 있다면 그 파일을 사용
    st.info("✅ 업로드된 파일을 사용합니다.")
    df = load_data(uploaded_file)
else:
    try:
        # 3. 업로드된 파일이 없으면 기본 데이터 사용
        st.info(f"📁 기본 데이터 파일 '{default_data_path}'를 사용합니다.")
        df = load_data(default_data_path)
    except FileNotFoundError:
        st.warning(f"⚠️ 기본 데이터 파일 '{default_data_path}'을 찾을 수 없습니다. 파일을 업로드해 주세요.")
        df = None

if df is not None:
    # 데이터 처리 및 분석
    proportions_df = get_mbti_proportions(df)
    
    if proportions_df is not None:
        # 각 MBTI 유형별로 비율이 가장 높은 국가 찾기
        top_countries_by_mbti = proportions_df.loc[proportions_df.groupby('mbti_type')['proportion'].idxmax()]
        
        # 전체 비율 기준으로 상위 10개 국가 정렬
        top_10_countries = top_countries_by_mbti.sort_values(by='proportion', ascending=False).head(10)
        
        st.subheader("업로드된 데이터 미리보기")
        st.dataframe(df.head())
        st.write("---")

        if not top_10_countries.empty:
            st.subheader("✨ MBTI 유형별 최고 비율 국가 Top 10")
            
            # Altair 차트 생성
            chart = alt.Chart(top_10_countries).mark_bar().encode(
                x=alt.X('proportion', axis=alt.Axis(title='비율', format='.1%')),
                y=alt.Y('country', sort='-x', axis=alt.Axis(title='국가')),
                tooltip=[
                    alt.Tooltip('country', title='국가'),
                    alt.Tooltip('mbti_type', title='MBTI 유형'),
                    alt.Tooltip('proportion', title='비율', format='.2%')
                ],
                color=alt.Color('mbti_type', title='MBTI 유형')
            ).properties(
                title="MBTI 유형별 최고 비율 국가 TOP 10"
            ).interactive()
            
            st.altair_chart(chart, use_container_width=True)

        else:
            st.warning("데이터 분석 결과가 없습니다. CSV 파일의 형식을 확인해 주세요.")
            
    else:
        st.error("업로드된 CSV 파일에 'country' 또는 'mbti_type' 컬럼이 포함되어 있는지 확인해 주세요.")
