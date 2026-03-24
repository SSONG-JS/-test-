import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="학원 성적 분석 앱", layout="wide")

st.title("📊 학원 성적 분석 앱")
st.write("엑셀 파일을 업로드하면 학생별/반별/과목별 성적을 분석할 수 있습니다.")

# -----------------------------
# 기본 설정
# -----------------------------
REQUIRED_COLUMNS = ["이름", "학년", "반", "시험명"]
SUBJECT_CANDIDATES = ["국어", "영어", "수학", "과학", "사회"]

# -----------------------------
# 함수
# -----------------------------
def load_data(uploaded_file):
    """업로드한 파일을 읽어서 DataFrame으로 반환"""
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    return df


def validate_columns(df):
    """필수 컬럼 존재 여부 확인"""
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    return missing


def get_subject_columns(df):
    """실제 데이터에 들어있는 과목 컬럼 찾기"""
    subjects = [col for col in SUBJECT_CANDIDATES if col in df.columns]
    return subjects


def convert_subjects_to_numeric(df, subject_cols):
    """과목 점수를 숫자로 변환"""
    for col in subject_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def apply_filters(df):
    """사이드바 필터 적용"""
    st.sidebar.header("🔎 필터")

    grade_options = ["전체"] + sorted(df["학년"].dropna().astype(str).unique().tolist())
    class_options = ["전체"] + sorted(df["반"].dropna().astype(str).unique().tolist())
    exam_options = ["전체"] + sorted(df["시험명"].dropna().astype(str).unique().tolist())

    selected_grade = st.sidebar.selectbox("학년 선택", grade_options)
    selected_class = st.sidebar.selectbox("반 선택", class_options)
    selected_exam = st.sidebar.selectbox("시험명 선택", exam_options)
    student_search = st.sidebar.text_input("학생 이름 검색")

    filtered_df = df.copy()

    if selected_grade != "전체":
        filtered_df = filtered_df[filtered_df["학년"].astype(str) == selected_grade]

    if selected_class != "전체":
        filtered_df = filtered_df[filtered_df["반"].astype(str) == selected_class]

    if selected_exam != "전체":
        filtered_df = filtered_df[filtered_df["시험명"].astype(str) == selected_exam]

    if student_search:
        filtered_df = filtered_df[
            filtered_df["이름"].astype(str).str.contains(student_search, case=False, na=False)
        ]

    return filtered_df, selected_grade, selected_class, selected_exam


def add_total_average(df, subject_cols):
    """총점과 평균 컬럼 추가"""
    df = df.copy()
    df["총점"] = df[subject_cols].sum(axis=1, skipna=True)
    df["평균"] = df[subject_cols].mean(axis=1, skipna=True).round(2)
    return df


def download_csv(df):
    """CSV 다운로드 버튼"""
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 필터된 데이터 CSV 다운로드",
        data=csv,
        file_name="성적분석결과.csv",
        mime="text/csv",
    )


# -----------------------------
# 샘플 양식 안내
# -----------------------------
with st.expander("엑셀 업로드 양식 예시 보기"):
    sample_df = pd.DataFrame({
        "이름": ["김민수", "이서연", "박지훈"],
        "학년": [1, 1, 2],
        "반": ["A", "A", "B"],
        "시험명": ["중간고사", "중간고사", "중간고사"],
        "국어": [85, 92, 78],
        "영어": [90, 88, 81],
        "수학": [95, 91, 84],
        "과학": [88, 85, 79],
        "사회": [82, 87, 80],
    })
    st.dataframe(sample_df, use_container_width=True)

uploaded_file = st.file_uploader("엑셀 파일(.xlsx, .xls) 또는 CSV 파일을 업로드하세요.", type=["xlsx", "xls", "csv"])

if uploaded_file is not None:
    try:
        df = load_data(uploaded_file)

        # 컬럼 공백 제거
        df.columns = [str(col).strip() for col in df.columns]

        # 필수 컬럼 확인
        missing_cols = validate_columns(df)
        if missing_cols:
            st.error(f"필수 컬럼이 없습니다: {missing_cols}")
            st.stop()

        # 과목 컬럼 찾기
        subject_cols = get_subject_columns(df)
        if not subject_cols:
            st.error("과목 컬럼이 없습니다. 예: 국어, 영어, 수학, 과학, 사회")
            st.stop()

        # 숫자 변환
        df = convert_subjects_to_numeric(df, subject_cols)

        # 총점/평균 추가
        df = add_total_average(df, subject_cols)

        # 필터 적용
        filtered_df, selected_grade, selected_class, selected_exam = apply_filters(df)

        st.subheader("📋 필터된 데이터")
        st.dataframe(filtered_df, use_container_width=True)

        if filtered_df.empty:
            st.warning("조건에 맞는 데이터가 없습니다.")
            st.stop()

        download_csv(filtered_df)

        # -----------------------------
        # 요약 지표
        # -----------------------------
        st.subheader("📌 요약 지표")

        total_students = filtered_df["이름"].nunique()
        overall_avg = filtered_df["평균"].mean().round(2)
        top_student = filtered_df.sort_values("총점", ascending=False).iloc[0]["이름"]
        top_score = filtered_df["총점"].max()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("학생 수", total_students)
        col2.metric("전체 평균", overall_avg)
        col3.metric("최고 총점", round(top_score, 2))
        col4.metric("최고점 학생", top_student)

        # -----------------------------
        # 과목별 평균
        # -----------------------------
        st.subheader("📚 과목별 평균")
        subject_avg = filtered_df[subject_cols].mean().round(2)
        subject_avg_df = pd.DataFrame({
            "과목": subject_avg.index,
            "평균점수": subject_avg.values
        })
        st.dataframe(subject_avg_df, use_container_width=True)

        fig1, ax1 = plt.subplots(figsize=(8, 4))
        ax1.bar(subject_avg_df["과목"], subject_avg_df["평균점수"])
        ax1.set_title("과목별 평균 점수")
        ax1.set_ylabel("점수")
        st.pyplot(fig1)

        # -----------------------------
        # 학생별 성적 분석
        # -----------------------------
        st.subheader("👤 학생별 성적 분석")
        student_names = sorted(filtered_df["이름"].dropna().astype(str).unique().tolist())
        selected_student = st.selectbox("학생 선택", student_names)

        student_df = filtered_df[filtered_df["이름"].astype(str) == selected_student]

        if not student_df.empty:
            st.write(f"### {selected_student} 학생 성적")

            student_display_cols = ["이름", "학년", "반", "시험명"] + subject_cols + ["총점", "평균"]
            st.dataframe(student_df[student_display_cols], use_container_width=True)

            # 가장 최근 행 기준으로 그래프
            latest_row = student_df.iloc[-1]
            student_scores = latest_row[subject_cols]

            fig2, ax2 = plt.subplots(figsize=(8, 4))
            ax2.bar(subject_cols, student_scores)
            ax2.set_title(f"{selected_student} 학생 과목별 점수")
            ax2.set_ylabel("점수")
            st.pyplot(fig2)

        # -----------------------------
        # 반별 평균 분석
        # -----------------------------
        st.subheader("🏫 반별 평균 분석")

        class_avg_df = (
            filtered_df.groupby("반")[subject_cols + ["총점", "평균"]]
            .mean()
            .round(2)
            .reset_index()
        )
        st.dataframe(class_avg_df, use_container_width=True)

        if len(class_avg_df) > 0:
            fig3, ax3 = plt.subplots(figsize=(8, 4))
            ax3.bar(class_avg_df["반"].astype(str), class_avg_df["평균"])
            ax3.set_title("반별 평균 점수")
            ax3.set_ylabel("평균")
            st.pyplot(fig3)

        # -----------------------------
        # 학생별 순위표
        # -----------------------------
        st.subheader("🏆 학생 순위표")

        rank_df = filtered_df[["이름", "학년", "반", "시험명", "총점", "평균"]].copy()
        rank_df = rank_df.sort_values(by=["총점", "평균"], ascending=False).reset_index(drop=True)
        rank_df.index = rank_df.index + 1
        rank_df.index.name = "순위"

        st.dataframe(rank_df, use_container_width=True)

    except Exception as e:
        st.error(f"파일을 처리하는 중 오류가 발생했습니다: {e}")

else:
    st.info("먼저 엑셀 파일 또는 CSV 파일을 업로드해주세요.")