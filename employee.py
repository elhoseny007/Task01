import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import base64

st.set_page_config(
    page_title="كيف - HR Analytics",
    layout="wide",
    page_icon="👥"
)

# ====================== CUSTOM CSS ======================
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117; 
    }
    .stApp, .stMarkdown, .stMetric, h1, h2, h3, h4, p, label, .css-1d391kg, .st-emotion-cache {
        color: #ffffff !important;
    }
    .header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: linear-gradient(90deg, #1e40af, #3b82f6);
        padding: 20px 40px;
        border-radius: 12px;
        margin-bottom: 25px;
    }
    .logo-text {
        font-size: 48px;
        font-weight: 900;
        color: white;
        margin: 0;
    }
    /* تحسين تصميم الكروت المتجاوبة */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 15px;
        margin-bottom: 30px;
    }
    .kpi-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-radius: 12px;
        padding: 20px 10px;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    /* تأثير الـ Hover المطلوب */
    .kpi-card:hover {
        transform: translateY(-8px);
        border-color: #60a5fa;
        box-shadow: 0 12px 25px rgba(59, 130, 246, 0.4);
        background: rgba(59, 130, 246, 0.15);
    }
    .kpi-icon {
        font-size: 32px;
        margin-bottom: 10px;
        display: block;
    }
    .kpi-value {
        font-size: 24px;
        font-weight: 700;
        color: #ffffff;
        margin: 5px 0;
    }
    .kpi-label {
        font-size: 12px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# ====================== HEADER WITH LOGO ======================
col_logo, col_title = st.columns([1, 4])

with col_logo:
    st.image(r"C:\Users\ELZAHBIA\Vs_code\Kayfa_logo.png", width=180)

with col_title:
    st.markdown("<h1 style='color:white; margin:10px 0;'>Employee Attrition Intelligence Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#bae6fd;'>كيف Analytics - Internship Program</p>", unsafe_allow_html=True)

@st.cache_data
def load_data():
    train = pd.read_csv(r'C:/Users/ELZAHBIA/AppData/Local/Temp/Rar$DRa8636.730/train.csv')
    test = pd.read_csv(r'C:/Users/ELZAHBIA/AppData/Local/Temp/Rar$DRa8636.3767/test.csv')
    df_full = pd.concat([train, test], ignore_index=True)
    
    if 'Employee ID' in df_full.columns:
        df_full.rename(columns={'Employee ID': 'Employee_ID'}, inplace=True)
    df_full.dropna(how='all', inplace=True)
    return df_full

df = load_data()

df['Attrition_Status'] = df['Attrition'].map({0: 'Stayed', 1: 'Left'})

# ====================== 4. SIDEBAR FILTERS ======================
st.sidebar.title("🎛️ Dashboard Filters")

selected_roles = st.sidebar.multiselect(
    "Select Job Roles:", 
    options=list(df['Job Role'].unique()), 
    default=list(df['Job Role'].unique())
)

selected_gender = st.sidebar.multiselect(
    "Select Gender:", 
    options=list(df['Gender'].unique()), 
    default=list(df['Gender'].unique())
)

filtered_df = df[df['Job Role'].isin(selected_roles) & df['Gender'].isin(selected_gender)]

COLOR_MAP = {'Stayed': '#3b82f6', 'Left': '#ef4444'}

# ====================== 5. HEADER & DYNAMIC KPIs ======================
st.markdown("A data-driven view into organizational health, turnover drivers, and demographic profiles.")

st.subheader("Quick Stats")

total_employees = filtered_df.shape[0]
avg_age = filtered_df['Age'].mean()
avg_income = filtered_df['Monthly Income'].mean()
avg_years = filtered_df['Years at Company'].mean()
avg_distance = filtered_df['Distance from Home'].mean()

attrition_counts = filtered_df['Attrition'].value_counts()
stayed_count = attrition_counts.get(0, 0)  
left_count = attrition_counts.get(1, 0)    

# ====================== NEW KPI LAYOUT USING MODERN CARDS ======================
# هنا تم بناء الكروت بالـ HTML والـ CSS لتعطي المظهر العصري وتأثير الـ Hover المطلوب بدلاً من st.metric الافتراضية
kpi_html = f"""
<div class="kpi-container">
    <div class="kpi-card">
        <span class="kpi-icon">👥</span>
        <div class="kpi-value">{total_employees:,}</div>
        <div class="kpi-label">Employees</div>
    </div>
    <div class="kpi-card">
        <span class="kpi-icon">🎂</span>
        <div class="kpi-value">{avg_age:.1f}</div>
        <div class="kpi-label">Avg Age</div>
    </div>
    <div class="kpi-card">
        <span class="kpi-icon">💰</span>
        <div class="kpi-value">${avg_income:,.0f}</div>
        <div class="kpi-label">Avg Income</div>
    </div>
    <div class="kpi-card">
        <span class="kpi-icon">📅</span>
        <div class="kpi-value">{avg_years:.1f}</div>
        <div class="kpi-label">Avg Years</div>
    </div>
    <div class="kpi-card">
        <span class="kpi-icon">📍</span>
        <div class="kpi-value">{avg_distance:.1f}</div>
        <div class="kpi-label">Avg Distance</div>
    </div>
    <div class="kpi-card" style="border-color: rgba(59, 130, 246, 0.5);">
        <span class="kpi-icon" style="color: #3b82f6;">✅</span>
        <div class="kpi-value" style="color: #3b82f6;">{stayed_count:,}</div>
        <div class="kpi-label">Stayed</div>
    </div>
    <div class="kpi-card" style="border-color: rgba(239, 68, 68, 0.5);">
        <span class="kpi-icon" style="color: #ef4444;">🚨</span>
        <div class="kpi-value" style="color: #ef4444;">{left_count:,}</div>
        <div class="kpi-label">Left</div>
    </div>
</div>
"""
st.markdown(kpi_html, unsafe_allow_html=True)


# ====================== 6. CHARTS GRID ORGANIZED BY TABS ======================
tab1, tab2, tab3 = st.tabs(["⏳ Longevity & Demographics", "💰 Role & Compensation", "👤 Personal Profiles"])

# ----------------- Tab 1: العمر والأقدمية -----------------
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        age_attr = filtered_df.groupby('Age')['Attrition'].value_counts().unstack(fill_value=0).reset_index()
        fig1 = px.line(
            age_attr, x='Age', y=age_attr.columns[1:], 
            title='Attrition Trend by Age',
            color_discrete_map=COLOR_MAP, template="plotly_dark"
        )
        fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig1, use_container_width=True)
        
    with col2:
        fig2 = px.histogram(
            filtered_df, x='Age', nbins=20, 
            title='Overall Age Distribution',
            color_discrete_sequence=['#6366f1'], template="plotly_dark"
        )
        fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    
    with col3:
        years_attr = filtered_df.groupby('Years at Company')['Attrition'].value_counts().unstack(fill_value=0).reset_index()
        fig3 = px.line(
            years_attr, x='Years at Company', y=years_attr.columns[1:], 
            title='Attrition by Years at Company',
            color_discrete_map=COLOR_MAP, template="plotly_dark"
        )
        fig3.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig3, use_container_width=True)
        
    with col4:
        distance_attr = filtered_df.groupby('Distance from Home')['Attrition'].value_counts().unstack(fill_value=0).reset_index()
        fig4 = px.bar(
            distance_attr, x='Distance from Home', y=distance_attr.columns[1:], 
            barmode='group', title='Attrition by Distance from Home (Miles)',
            color_discrete_map=COLOR_MAP, template="plotly_dark"
        )
        fig4.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig4, use_container_width=True)

# ----------------- Tab 2: الوظائف والرواتب -----------------
with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        filtered_df['Income Range'] = pd.cut(filtered_df['Monthly Income'], bins=10)
        filtered_df['Income Range'] = filtered_df['Income Range'].astype(str)
        income_attr = filtered_df.groupby('Income Range')['Attrition'].value_counts().unstack(fill_value=0).reset_index()
        
        fig5 = px.bar(
            income_attr, x='Income Range', y=income_attr.columns[1:], 
            barmode='group', title='Attrition Impact by Monthly Income Ranges',
            color_discrete_map=COLOR_MAP, template="plotly_dark"
        )
        fig5.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis_tickangle=-45)
        st.plotly_chart(fig5, use_container_width=True)
        
    with col2:
        company_attr = filtered_df.groupby('Company Size')['Attrition'].value_counts().unstack(fill_value=0).reset_index()
        fig6 = px.bar(
            company_attr, x='Company Size', y=company_attr.columns[1:], 
            barmode='group', title='Attrition Rate by Company Size',
            color_discrete_map=COLOR_MAP, template="plotly_dark"
        )
        fig6.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig6, use_container_width=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
 
    col3, col4 = st.columns(2)
    
    with col3:
        job_attr = filtered_df.groupby('Job Role')['Attrition'].value_counts().unstack(fill_value=0).reset_index()
        
        satisfaction_map = {'Very Low': 1, 'Low': 2, 'Medium': 3, 'High': 4}
        df_temp = filtered_df.copy()
        if df_temp['Job Satisfaction'].dtype == 'object':
            df_temp['Job_Sat_Num'] = df_temp['Job Satisfaction'].map(satisfaction_map)
        else:
            df_temp['Job_Sat_Num'] = df_temp['Job Satisfaction']
            
        job_sat = df_temp.groupby('Job Role')['Job_Sat_Num'].mean().reset_index()
        merged_data = pd.merge(job_attr, job_sat, on='Job Role')

        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        fig7 = make_subplots(specs=[[{"secondary_y": True}]])

        if 'Stayed' in merged_data.columns:
            fig7.add_trace(go.Bar(x=merged_data['Job Role'], y=merged_data['Stayed'], name="Stayed", marker_color='#3b82f6'), secondary_y=False)
        if 'Left' in merged_data.columns:
            fig7.add_trace(go.Bar(x=merged_data['Job Role'], y=merged_data['Left'], name="Left", marker_color='#ef4444'), secondary_y=False)

        fig7.add_trace(
            go.Scatter(x=merged_data['Job Role'], y=merged_data['Job_Sat_Num'], name="Avg Job Satisfaction", mode="lines+markers", line=dict(color="#f59e0b", width=3), marker=dict(size=8)),
            secondary_y=True
        )

        fig7.update_layout(
            title_text='Attrition Breakdown & Avg Job Satisfaction by Job Role',
            template="plotly_dark", barmode='group', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig7.update_yaxes(title_text="Employee Count", secondary_y=False)
        fig7.update_yaxes(title_text="Satisfaction Score (1-4)", secondary_y=True, range=[1, 4])
        st.plotly_chart(fig7, use_container_width=True)
        
    with col4:
        remote_attr = filtered_df.groupby('Remote Work')['Attrition'].value_counts().unstack(fill_value=0).reset_index()
        fig8 = px.bar(
            remote_attr, x='Remote Work', y=remote_attr.columns[1:], 
            barmode='group', title='Attrition: Remote Work vs Onsite Environment',
            color_discrete_map=COLOR_MAP, template="plotly_dark"
        )
        fig8.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig8, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col5, col6 = st.columns(2)
    
    with col5:
        seniors = filtered_df.groupby('Job Level')['Attrition'].value_counts().unstack(fill_value=0).reset_index()
        fig9 = px.bar(
            seniors, x='Job Level', y=seniors.columns[1:], 
            barmode='group', title='Attrition by Job Level',
            color_discrete_map=COLOR_MAP, template="plotly_dark"
        )
        fig9.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig9, use_container_width=True)

# ----------------- Tab 3: البيانات الشخصية -----------------
with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        gender_attr = filtered_df.groupby(['Gender', 'Attrition']).size().unstack(fill_value=0).reset_index()

        for status in ['Stayed', 'Left']:
            if status not in gender_attr.columns:
                gender_attr[status] = 0
        fig10 = px.bar(
            gender_attr, 
            x='Gender', 
            y=['Stayed', 'Left'], 
            barmode='group', 
            title='Attrition Analysis by Gender',
            color_discrete_map=COLOR_MAP, 
            template="plotly_dark"
        )
        fig10.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_type='category', 
            yaxis_title="Number of Employees"
        )
        st.plotly_chart(fig10, use_container_width=True)
        
    with col2:
        marital_attr = filtered_df.groupby(['Marital Status', 'Attrition']).size().unstack(fill_value=0)

        for status in ['Stayed', 'Left']:
            if status not in marital_attr.columns:
                marital_attr[status] = 0
            
        marital_attr = marital_attr.reset_index()

        if 'Left' in marital_attr.columns and marital_attr['Left'].sum() > 0:
            fig11 = px.pie(
                marital_attr,
                names='Marital Status',
                values='Left',  
                title='نسبة الاستقالة بناءً على الحالة الاجتماعية'
            )
            st.plotly_chart(fig11, use_container_width=True)
        else:
            st.info("لا توجد بيانات موظفين مغادرين (Left) لعرضها.")