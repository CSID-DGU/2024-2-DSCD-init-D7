import streamlit as st
import matplotlib.pyplot as plt
import os
import sys
import base64
from io import BytesIO

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from NLP.extract.extract_okr import extract_okr

# 예제 데이터: score 및 팀 멤버 정의
score = 91.17
members = [
    {"name": "강성지", "role": "PM(9년차)", "skills": "Agile, Scrum"},
    {"name": "구동현", "role": "UI/UX(3년차)", "skills": "Figma, Adobe"},
    {"name": "김승현", "role": "D_Eng(4년차)", "skills": "SQL, Python"},
    {"name": "전현재", "role": "F_Dev(2년차)", "skills": "React, Vue.js"},
    {"name": "유근태", "role": "B_Dev(2년차)", "skills": "Node.js"}
]

# Base64로 이미지 인코딩
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Predictive Performance 원형 그래프를 PNG로 저장하여 Base64로 인코딩
def create_circular_performance_chart(score):
    fig, ax = plt.subplots(figsize=(3, 3), subplot_kw=dict(aspect="equal"))
    colors = ["red", "lightgray"]
    data = [score, 100 - score]
    wedges, texts = ax.pie(data, colors=colors, startangle=90, wedgeprops=dict(width=0.3, edgecolor="w"))
    ax.text(0, 0, f"{score}%", ha='center', va='center', fontsize=14, fontweight='bold')
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", transparent=True)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

# 페이지 설정
st.set_page_config(layout="wide")

# CSS 스타일 정의
st.markdown(
    """
    <style>
    .box {
        border: 2px solid #e6e6e6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 12px rgba(0, 0, 0, 0.1);
        background-color: white;
        margin-bottom: 20px;
        height: 350px;
        width: 100%;
    }
    .title-box {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .section-title {
        font-size: 24px;
        font-weight: bold;
        margin-top: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 상태 관리: 대시보드 전환 여부 확인
if 'dashboard' not in st.session_state:
    st.session_state['dashboard'] = False

if not st.session_state['dashboard']:
    # 파일 업로드 페이지
    st.title("Upload Files")
    file_title = st.text_input("Title", "Input Title")
    uploaded_file = st.file_uploader("Attached Document", type=['pdf', 'docx', 'hwp'], label_visibility="collapsed")

    if st.button("Upload", help="Click to upload your file"):
        if uploaded_file is not None and file_title:
            save_path = os.path.join("uploaded_files", uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.session_state['uploaded_file_path'] = save_path
            st.session_state['file_title'] = file_title
            st.session_state['dashboard'] = True
            
            st.success(f"{uploaded_file.name} 파일이 업로드되었습니다.")
        else:
            st.warning("제목과 파일을 모두 입력해 주세요.")

else:
    # 대시보드 페이지
    st.title("Dashboard")
    final_okr_list = extract_okr(st.session_state['uploaded_file_path'])

    # 상단 프로젝트 설명 및 목표 섹션
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            f"""
            <div class="box">
                <div class="title-box">Title: {st.session_state['file_title']}</div>
                <p><strong>Content:</strong> {final_okr_list[0][0]}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div class="box">
                <div class="title-box">Objective and Key Results</div>
                <p><strong>Objective:</strong> {final_okr_list[0][1]}</p>
                <p><strong>Key Result 1:</strong> {final_okr_list[0][2]}</p>
                <p><strong>Key Result 2:</strong> {final_okr_list[0][3]}</p>
                <p><strong>Key Result 3:</strong> {final_okr_list[0][4]}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 팀 멤버 섹션
    st.markdown('<div class="section-title">Team Members</div>', unsafe_allow_html=True)
    member_cols = st.columns(5)
    for col, member in zip(member_cols, members):
        col.markdown(
            f"""
            <div class="box" style="text-align: center;">
                <p><strong>{member['name']}</strong></p>
                <p>{member['role']}</p>
                <p>{member['skills']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 중간 성능 그래프 섹션
    st.markdown('<div class="section-title">Project Insights</div>', unsafe_allow_html=True)
    insights_col1, insights_col2 = st.columns([1, 1])

    # Predictive Performance 그래프 생성 및 표시
    with insights_col1:
        performance_chart_base64 = create_circular_performance_chart(score)
        st.markdown(
            f"""
            <div class="box" style="text-align: center;">
                <h4>Predictive Performance</h4>
                <img src="data:image/png;base64,{performance_chart_base64}" width="200">
            </div>
            """,
            unsafe_allow_html=True
        )

    # Feature Importance 그래프 (이미지 파일로 표시)
    with insights_col2:
        feature_importance_image_base64 = get_base64_image("./image/feature_importance.png")
        st.markdown(
            f"""
            <div class="box" style="text-align: center;">
                <h4>Feature Importance</h4>
                <img src="data:image/png;base64,{feature_importance_image_base64}" width="400">
            </div>
            """,
            unsafe_allow_html=True
        )

    # Additional Insights 섹션
    st.markdown('<div class="section-title">Additional Insights</div>', unsafe_allow_html=True)
    additional_col1, additional_col2 = st.columns([1, 1])

    # Score Comparison by Team 그래프 표시
    score_comparison_image_base64 = get_base64_image("./image/score_comparison.png")
    with additional_col1:
        st.markdown(
            f"""
            <div class="box" style="text-align: center;">
                <h4>Score Comparison by Team</h4>
                <img src="data:image/png;base64,{score_comparison_image_base64}" width="400">
            </div>
            """,
            unsafe_allow_html=True
        )

    # Team Color 원형 그래프 표시
    team_color_image_base64 = get_base64_image("./image/team_color.png")
    with additional_col2:
        st.markdown(
            f"""
            <div class="box" style="text-align: center;">
                <h4>Team Color</h4>
                <img src="data:image/png;base64,{team_color_image_base64}" width="400">
            </div>
            """,
            unsafe_allow_html=True
        )

    # Field Results 그래프 표시
    field_result_image_base64 = get_base64_image("./image/field_result.png")
    st.markdown(
        f"""
        <div class="box" style="text-align: center; height: 350px;">
            <h4>Field Results</h4>
            <img src="data:image/png;base64,{field_result_image_base64}" width="800">
        </div>
        """,
        unsafe_allow_html=True
    )
