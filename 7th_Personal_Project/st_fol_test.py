# 라이브러리 로드
import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import MarkerCluster

import pandas as pd
import numpy as np

# 위경도 변환
from geopy.geocoders import Nominatim
# ===============================================================
# Functions
# 주소를 위경도로 변환해주는 함수
def geocoding(address: pd.Series) -> [float, float]:
    geo = geo_local.geocode(address)
    x_y = [geo.latitude, geo.longitude]
    return x_y

# 지도에 마커 추가
def add_marker(df):
    for idx, _ in enumerate(df.values):
        lat = df['latitude'][idx]
        long = df['longitude'][idx]
        
        name_1 = df['이름'][idx]
        job_1 = df['직업/전공'][idx]
        comm_1 = df['커뮤'][idx]
        
        popup_1 = folium.Popup(f'{name_1} : {job_1}',
                               max_width=80)
        tooltip_1 = f'{name_1} : {comm_1}'

        
        # 커뮤별 아이콘 색 분류, circle 적용 불가
        if comm_1 == 'Z':
            color = "blue"
        elif comm_1 == 'M':
            color = "green"
        else:
            color = "red"
            
        # folium.Marker([latitude_1, longitude_1],
        #               popup=popup_1,
        #               tooltip=tooltip_1
        #              ).add_to(m)
        
        folium.Circle([lat, long],
                      popup=popup_1,
                      tooltip=tooltip_1,
                      radius=300
                     ).add_to(st.session_state.fol_map)

# 클러스터 마커 추가        
def add_cluster(df):
    # 클러스터 적용
    marker_cluster = MarkerCluster().add_to(st.session_state.fol_map)
    
    for idx, _ in enumerate(df.values):
        # 위경도
        lat = df['latitude'][idx]
        long = df['longitude'][idx]
        
        # 추가 정보
        name_1 = df['이름'][idx]
        job_1 = df['직업/전공'][idx]
        comm_1 = df['커뮤'][idx]
        popup_1 = folium.Popup(f'{name_1} : {job_1}',
                               max_width=80)
        tooltip_1 = f'{name_1} : {comm_1}'
        
        # 커뮤별 아이콘 색 분류
        if comm_1 == 'Z':
            color = "blue"
        elif comm_1 == 'M':
            color = "green"
        else:
            color = "red"
        
        # 마커 추가
        folium.Marker([lat, long], 
                      icon = folium.Icon(color=color),   # color='darkblue' -> 아보트블루
                      popup=popup_1,
                      tooltip=tooltip_1,
                     ).add_to(marker_cluster)
        
# ===============================================================
# Streamlit Session State Initialization
if 'fol_map' not in st.session_state:
    st.session_state.fol_map = []
    

# ===============================================================
# Main loop

# Main page title
st.set_page_config(page_title="Streamlit + Folium 으로 회원정보 지도 만들기")
st.title('📸 Streamlit + Folium 으로 회원정보 지도 만들기')

# Sidebar
page = st.sidebar.radio(
    "Select page", 
    ["File upload", "Circle marker", "Cluster marker"], 
    index=0,
)

# Page 1 File upload
if page == 'File upload':
# file upload button - csv, xlsx 파일형식

    st.header('File upload')
    uploaded_file = st.file_uploader("Choose a file - .csv or .xlsx only", type=['csv', 'xlsx'])
    
    if uploaded_file is not None:
        with st.spinner('Processing! Wait for it...'):
            # 데이터프레임 전처리
            df = pd.read_excel(uploaded_file)
            df = pd.DataFrame(df, columns=['이름', '커뮤', '주소', '직업/전공'])

            df['city'] = df['주소'].str.split().str[0]   # 시별 분류
            df['district'] = df['주소'].str.split().str[1]   # 지역구별 분류
            df['address_geo'] = df['city'] + ' ' + df['district']   # 상세 주소 
            st.session_state.df = df.drop(['city', 'district'], axis=1)   # 불필요한 컬럼 제거

            # 상세 주소로 위경도 변환
            geo_local = Nominatim(user_agent='South Korea')
            latitude, longitude = [], []

            for idx, add in enumerate(st.session_state.df['address_geo']):
                # print(idx, add)
                latitude.append(geocoding(add)[0])
                longitude.append(geocoding(add)[1])

            st.session_state.df['latitude'] = latitude
            st.session_state.df['longitude'] = longitude

        st.success('Done!')   # Spinner 완료
        st.write(st.session_state.df)   # plot dataframe

# Page 2 Circle marker
elif page == 'Circle marker':
    st.header('Circle marker map')
    
    # reset map instance
    st.session_state.fol_map = folium.Map(location=[36, 128],   # 초기 위치 지정
               zoom_start=7,
               # width=750,
               # height=500
              )
    
    add_marker(st.session_state.df)
    # call to render Folium map in Streamlit
    with st.spinner('Wait for it...'):
        st_data = st_folium(st.session_state.fol_map, width = 725)
        st.write(st.session_state.df)
    st.success('Done!')
    

# Page 3 Cluster marker
elif page == 'Cluster marker':
    st.header('Cluster marker map')
    
    # reset map instance
    st.session_state.fol_map = folium.Map(location=[36, 128],   # 초기 위치 지정
               zoom_start=7,
               # width=750,
               # height=500
              )
    
    add_cluster(st.session_state.df)    
    # call to render Folium map in Streamlit
    with st.spinner('Wait for it...'):
        st_data = st_folium(st.session_state.fol_map, width = 725)
        st.write(st.session_state.df)
    st.success('Done!')
