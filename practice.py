import streamlit as st
import pandas as pd

# UI 레이아웃 설정
st.set_page_config(layout="wide")

st.title('띠장 해체단계별 합벽의 구조안정성 검토')

st.sidebar.header('합벽부재 기본정보')
fck = st.sidebar.number_input('콘크리트 설계강도 (MPa)', value=18)
fy = st.sidebar.number_input('fy (MPa)', value=550)
fsy = st.sidebar.number_input('fsy (MPa)', value=500)
h = st.sidebar.number_input('벽체두께 (mm)', value=600)
d = st.sidebar.number_input('벽체주철근까지의 거리(d) (mm)', value=540)

# 철근 선택 항목 만들기
rebar_areas = {
    "D10": 71.3,
    "D13": 126.7,
    "D16": 198.6,
    "D19": 286.5,
    "D22": 387.1,
    "D25": 506.7,
    "D29": 642.4,
}

# 전단철근
shear_diameter = st.sidebar.selectbox('전단철근 직경 (mm)', list(rebar_areas.keys()))
selected_shear_area = rebar_areas[shear_diameter]
st.sidebar.write(f"Selected Shear Reinforcement Area: {selected_shear_area} mm²")

shear_spacing_H = st.sidebar.number_input('수평전단보강근 간격 (mm)', value=200)
shear_spacing_V = st.sidebar.number_input('수직전단보강근 간격 (mm)', value=200)

# 주철근
main_diameter = st.sidebar.selectbox('주철근 직경 (mm)', list(rebar_areas.keys()))
selected_main_area = rebar_areas[main_diameter]
st.sidebar.write(f"Selected Main Reinforcement Area: {selected_main_area} mm²")

main_spacing = st.sidebar.number_input('주철근 간격 (mm)', value=200)

# 작용 외력 산정 표시 및 입력 받기
st.header('외력 산정을 위한 토압입력')
L2 = st.number_input('L2(존치띠장-벽체사이 간격) (m)', value=4.0)  # 띠장-벽체사이 거리
L1 = st.number_input('L1(타설높이) (m)', value=2.5)  # 타설높이
S1 = st.number_input('S1 (kN/m2)', value=23.9)  # 토압1
S2 = st.number_input('S2 (kN/m2)', value=46.0)  # 토압2
S3 = st.number_input('S3 (kN/m2)', value=30.4)  # 토압3

# 토압에 의한 작용 외력 계산
M1_1 = min(S2, S3) * L1 ** 2 / 2
V1_1 = min(S2, S3) * L1
M1_2 = 0.5 * abs(S3 - S2) * L1 ** 2 / 2
V1_2 = 0.5 * abs(S3 - S2) * L1
M1 = M1_1 + M1_2
V1 = V1_1 + V1_2

R1 = min(S1, S2) * L2
R2 = 0.5 * abs(S1 - S2) * L2
R = R1 + R2
M2 = R * L1
V2 = R

# 데이터 처리 및 계산 로직 (예시로 간단한 연산 추가)
st.header('작용 휨 및 전단외력 산정')
Mu = 1.8 * M1 + 1.2 * M2 
Vu = 1.8 * V1 + 1.2 * V2
st.write(f'Mu: {Mu:.1f} kNm')
st.write(f'Vu: {Vu:.1f} kN')

# 부재내력 산정 및 구조안정성 검토 입력
st.header('부재내력 산정 및 구조안정성 검토')

st.subheader('전단강도 검토')
if selected_shear_area is not None:
    shear_rebar_area = (1000 / shear_spacing_H) * selected_shear_area
    shear_strength = 0.75 * (1/6) * (fck ** 0.5) + (0.75 * shear_rebar_area * fsy * d / shear_spacing_V / 1000)
    st.write(f'ΦVn: {shear_strength:.1f} kN')
    if shear_strength >= Vu:
        st.write(f'Vu/ΦVn = {Vu/shear_strength:.2f} → O.K')
    else:
        st.write(f'Vu/ΦVn = {Vu/shear_strength:.2f} → Shear Reinforcement Required')

st.subheader('휨강도 검토')
if selected_main_area is not None:
    main_rebar_area = selected_main_area * (1000 / main_spacing)
    a = (main_rebar_area * fy) / (0.85 * fck * 1000)
    flexural_strength = 0.85 * main_rebar_area * fy * (d - a / 2) * 10 ** -6
    if flexural_strength >= Mu:
        st.write(f'Mu/ΦMn = {Mu/flexural_strength:.2f} → O.K')
    else:
        st.write(f'Mu/ΦMn = {Mu/flexural_strength:.2f} → Main Reinforcement Required')

