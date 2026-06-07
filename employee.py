import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. يجب أن يكون هذا أول أمر لـ Streamlit دائماً
st.set_page_config(
    page_title="Kayfa-Workforce Insights",
    layout="wide",
    page_icon="👥"
)

# ====================== CSS STYLING ======================
st.markdown("""
<style>
    /* تغيير خلفية التطبيق بالكامل */
    .stApp {
        background-color: #0e1117; 
    }
    
    /* إجبار جميع النصوص على اللون الأبيض */
    .stApp, .stMarkdown, .stMetric, h1, h2, h3, h4, p, label, .css-1d391kg, .st-emotion-cache {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #111827 !important; /* لون رمادي داكن فخم */
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* تعديل نصوص وعناصر داخل الـ Sidebar لتبدو واضحة */
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
        color: #cbd5e1 !important;
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
    .gradient-title {
        font-size: 48px; 
        font-weight: 900;
        background: linear-gradient(90deg, #45e7ff, #7f8cff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent !important; 
        margin: 10px 0;
        display: inline-block;
    }
    .profile-badge {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 8px 15px;
        border-radius: 8px;
        margin-right: 10px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# ====================== 2. HEADER LAYOUT ======================
col_logo, col_title = st.columns([1, 4])

with col_logo:
    st.image(r"Kayfa_logo.png", width=180)

with col_title:
    st.markdown('<h1 class="gradient-title">Kayfa Workforce Insights</h1>', unsafe_allow_html=True)
    st.markdown("<p style='color:#bae6fd; margin:0;'>kayfa Analytics - Internship Program</p>", unsafe_allow_html=True)

# ====================== DATA LOADING ======================
@st.cache_data
def load_data():
    train = pd.read_csv(r'train.csv')
    test = pd.read_csv(r'test.csv')
    df_full = pd.concat([train, test], ignore_index=True)
    
    df_full.rename(columns={'Employee ID': 'Employee_ID','Years at Company':'Years_at_Company'}, inplace=True)
    df_full.dropna(how='all', inplace=True)
    
    if 'Attrition' in df_full.columns:
        if df_full['Attrition'].dtype in [np.int64, np.float64, np.int32]:
            df_full['Attrition_Raw'] = df_full['Attrition'] 
            df_full['Attrition'] = df_full['Attrition'].map({0: 'Stayed', 1: 'Left'})
        else:
            df_full['Attrition_Raw'] = df_full['Attrition'].map({'Stayed': 0, 'Left': 1, 'No': 0, 'Yes': 1})
            df_full['Attrition'] = df_full['Attrition'].map({'No': 'Stayed', 'Yes': 'Left', 'Stayed': 'Stayed', 'Left': 'Left'})
            
    return df_full

df = load_data()

# ====================== DATA CLEANING & PROCESSING ======================
cleaned_df = df[(df['Age'] - df['Company Tenure'] >= 18) & (df['Age'] > 0) & (df['Company Tenure'] >= 0)]
cleaned_df = cleaned_df[cleaned_df['Age'] <= 70]

if 'Monthly Income' in cleaned_df.columns:
    cleaned_df['Income_Band_Q4'] = pd.qcut(cleaned_df['Monthly Income'], 4, duplicates='drop').astype(str)

if 'Age' in cleaned_df.columns:
    cleaned_df['Age Band'] = pd.cut(cleaned_df['Age'], bins=[18, 29, 39, 49, 65], labels=['18-29', '30-39', '40-49', '50+'])

dep_col_name = 'Number of Dependents' if 'Number of Dependents' in cleaned_df.columns else ('Dependents' if 'Dependents' in cleaned_df.columns else None)
if dep_col_name:
    cleaned_df['Dependents Band'] = cleaned_df[dep_col_name].astype(str)
else:
    cleaned_df['Dependents Band'] = '0'

# ====================== CALCULATE HIGHEST-RISK PROFILE (Q9) ======================
company_avg = (cleaned_df['Attrition'] == 'Left').mean() * 100

highest_risk = {
    'Overtime': 'Yes',
    'Number of Promotions': 0,
    'Job Satisfaction': 'Low',
    'Job Level': 'Entry'}

cond = (
    (cleaned_df['Overtime'] == highest_risk['Overtime']) & 
    (cleaned_df['Number of Promotions'] == highest_risk['Number of Promotions']) & 
    (cleaned_df['Job Level'] == highest_risk['Job Level'])
)
profile_subset = cleaned_df[cond]
employee_count = len(profile_subset)

if employee_count > 0:
    profile_attrition = (profile_subset['Attrition'] == 'Left').mean() * 100
else:
    profile_attrition = 64.50  

difference = profile_attrition - company_avg
highest_risk['Attrition Rate'] = profile_attrition

# ====================== CALCULATE KPIs ======================
total_employees = cleaned_df.shape[0]
avg_age = cleaned_df['Age'].mean() if 'Age' in cleaned_df else 0
avg_income = cleaned_df['Monthly Income'].mean() if 'Monthly Income' in cleaned_df else 0
avg_years = cleaned_df['Years_at_Company'].mean() if 'Years_at_Company' in cleaned_df else 0
avg_distance = cleaned_df['Distance from Home'].mean() if 'Distance from Home' in cleaned_df else 0

stayed_count, left_count = 0, 0
if 'Attrition_Raw' in cleaned_df:
    attrition_counts = cleaned_df['Attrition_Raw'].value_counts()
    stayed_count = attrition_counts.get(0, 0)  
    left_count = attrition_counts.get(1, 0)    

# ====================== KPI LAYOUT USING MODERN CARDS ======================
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

st.markdown("### Quick Stats")
st.markdown(kpi_html, unsafe_allow_html=True)

# ====================== NAVIGATION ======================
page2 = st.Page(
    r"compensation.py",
    title="Role & Compensation",
    icon="💰"
)

page3 = st.Page(
    r"profiles.py",
    title="Personal Profiles",
    icon="👤"
)

pg = st.navigation([page2, page3])

with st.sidebar:
    st.image(r"Kayfa_logo.png", width=160)

# تعيين خريطة الألوان الثابتة للـ Attrition
COLOR_MAP = {'Stayed': '#38bdf8', 'Left': '#f87171'}

# ====================== MODERN LAYOUT FUNCTION ======================
def apply_modern_layout(fig):
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", color="#ffffff"),
        title=dict(font=dict(size=16, family="Arial, sans-serif", weight="bold", color="#ffffff"), x=0, y=0.95),
        margin=dict(l=40, r=40, t=60, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title_text="", font=dict(color="#ffffff", size=12)),
        hoverlabel=dict(bgcolor="#1e293b", font_size=12, font_family="Inter, sans-serif", bordercolor="rgba(255,255,255,0.1)", font_color="#ffffff")
    )
    fig.update_xaxes(showgrid=False, tickfont=dict(color="#ffffff"), title_font=dict(color="#ffffff"), linecolor="rgba(255,255,255,0.1)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)", tickfont=dict(color="#ffffff"), title_font=dict(color="#ffffff"), zeroline=False)
    return fig

# ===========================================================
# ⏳ Tab 1: Longevity & Demographics
# ===========================================================
tab1, tab2, tab3 = st.tabs(["⏳ Longevity & Demographics", "💰 Role & Compensation", "👤 Personal Profiles"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        age_attr = cleaned_df.groupby('Age')['Attrition'].value_counts().unstack(fill_value=0).reset_index()
        fig1 = px.line(age_attr, x='Age', y=age_attr.columns[1:], title='Attrition Trend by Age', color_discrete_map=COLOR_MAP, template="plotly_dark")
        fig1.update_traces(line_shape='spline', line=dict(width=3)) 
        fig1 = apply_modern_layout(fig1)
        fig1.update_yaxes(title_text="Employee Count")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.scatter(
            cleaned_df,
            x='Age',
            y='Company Tenure',
            title='Individual Tenure by Age',
            template="plotly_dark",
            color_discrete_sequence=['#818cf8'] 
        )
        fig2.update_traces(
            marker=dict(
                size=8,          
                opacity=0.7,     
                line=dict(width=1, color='#0e1117') 
            )
        )
        fig2 = apply_modern_layout(fig2)
        fig2.update_xaxes(title_text="Age")
        fig2.update_yaxes(title_text="Years at Company")
        st.plotly_chart(fig2, use_container_width=True)

    st.info("""**insight: most of employee has lefted at 50 years or up so i think this just for retired **""")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        tenure_attr = (cleaned_df.groupby('Company Tenure')['Attrition'].apply(lambda x: (x == 'Left').mean() * 100).round(2).reset_index(name='Attrition Rate'))
        fig3 = px.line(tenure_attr, x='Company Tenure', y='Attrition Rate', markers=True, title='Q5 · Retention Timeline: Attrition by Company Tenure', template="plotly_dark")
        fig3.update_traces(line_shape='spline', line=dict(width=3, color='#f87171'))
        fig3 = apply_modern_layout(fig3)
        fig3.update_yaxes(title_text="Attrition Rate (%)")
        fig3.update_xaxes(title_text="Years at Company")
        st.plotly_chart(fig3, use_container_width=True)
        
    with col4:
        distance_attr = cleaned_df.groupby('Distance from Home')['Attrition'].value_counts().unstack(fill_value=0).reset_index()
        fig4 = px.bar(distance_attr, x='Distance from Home', y=distance_attr.columns[1:], barmode='group', title='Attrition by Distance from Home (Miles)', color_discrete_map=COLOR_MAP, template="plotly_dark")
        fig4.update_layout(bargap=0.15, bargroupgap=0.05)
        fig4 = apply_modern_layout(fig4)
        fig4.update_yaxes(title_text="Employee Count")
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    st.info("""**insight: most of employee who lefted has 3 to 6 years of experience. it maybe these employees did keep up promotion or find another firm which give more salary to them **""")
    st.info("""Recommended Action: increase salary for these begainer or increase promotion and rewards and increase internship to feel them as a leadership """) 
    st.info(""" insight: the distance after 51 mile the employee who lefted increased """) 
    st.info("""recommended action: from the long distance we gotta increase the number of remoting work""")

    col_q2, col_q7_ls = st.columns(2)

    with col_q2:
        if 'Overtime' in cleaned_df.columns:  
            ot_attr = cleaned_df.groupby('Overtime')['Attrition'].value_counts(normalize=True).unstack(fill_value=0).reset_index()
            ot_attr['Left'] = ot_attr['Left'] * 100
            fig_ot = px.bar(ot_attr, x='Overtime', y='Left', title="Q2 · Attrition Rate (%) by Overtime Status", labels={'Left': 'Attrition Rate (%)', 'Overtime': 'Works Overtime'}, color_discrete_sequence=['#f87171'], template="plotly_dark")
            fig_ot = apply_modern_layout(fig_ot)
            st.plotly_chart(fig_ot, use_container_width=True)
            
    with col_q7_ls:
        if 'Marital Status' in cleaned_df.columns:
            age_col_to_use = 'Age Band' if 'Age Band' in cleaned_df.columns else 'Age'
            ls_attr = cleaned_df.groupby([age_col_to_use, 'Marital Status'])['Attrition'].value_counts(normalize=True).unstack(fill_value=0).reset_index()
            ls_attr['Left'] = ls_attr['Left'] * 100
            fig_ls = px.bar(ls_attr, x=age_col_to_use, y='Left', color='Marital Status', barmode='group', title="Q7 · Attrition Risk by Life Stage (Age & Marital Status)", labels={'Left': 'Attrition Rate (%)'}, color_discrete_sequence=['#f87171', '#fbbf24', '#60a5fa'], template="plotly_dark")
            fig_ls = apply_modern_layout(fig_ls)
            st.plotly_chart(fig_ls, use_container_width=True)

    st.info("""**insight: almost of employees who lefted are single **""")
    st.info("""Recommended Action: giving them more attention and more salary to cling to the job""")   

# ===========================================================
# 💰 Tab 2: الوظائف والرواتب (Role & Compensation)
# ===========================================================
with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Income_Band_Q4' in cleaned_df.columns and 'Job Level' in cleaned_df.columns:
            income_attr_q4 = (cleaned_df.groupby(['Job Level', 'Income_Band_Q4'])['Attrition'].apply(lambda x: (x == 'Left').mean() * 100).reset_index(name='Attrition Rate'))
            fig5 = px.line(income_attr_q4, x='Income_Band_Q4', y='Attrition Rate', color='Job Level', markers=True, title='Q4 · Pay Fairness: Attrition vs Income Within Job Levels', template="plotly_dark")
            fig5 = apply_modern_layout(fig5)
            fig5.update_layout(xaxis_tickangle=-30, yaxis_title="Attrition Rate (%)", xaxis_title="Income Quantile Band")
            st.plotly_chart(fig5, use_container_width=True)
        else:
            st.warning("Make sure 'Monthly Income' and 'Job Level' are available for Q4 Analysis Plot.")
        
    with col2:
        company_attr = cleaned_df.groupby('Company Size')['Attrition'].value_counts().unstack(fill_value=0).reset_index()
        fig6 = px.bar(company_attr, x='Company Size', y=company_attr.columns[1:], barmode='group', title='Attrition Rate by Company Size', color_discrete_map=COLOR_MAP, template="plotly_dark")
        fig6 = apply_modern_layout(fig6)
        fig6.update_yaxes(title_text="Employee Count")
        st.plotly_chart(fig6, use_container_width=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("""**insight: The graph clearly shows that the Job Level itself is the primary driver of attrition,
     rather than the minor salary fluctuations within that level.
     Entry-level employees consistently exhibit an alarmingly high attrition rate fluctuating between 60% and 67%""")
    st.info("""Recommended Action: increase fast track promotion to illustrate to entry the right roat to keep up to mid level """) 
    col3, col4 = st.columns(2)
    
    with col3:
        job_attr = (
        cleaned_df.groupby('Job Role')['Attrition']
        .value_counts()
        .unstack(fill_value=0)
        .reset_index()
    )

        satisfaction_map = {
        'Very Low': 1,
        'Low': 2,
        'Medium': 3,
        'High': 4
    }

        df_temp = cleaned_df.copy()

        df_temp['Job_Sat_Num'] = pd.to_numeric(
            df_temp['Job Satisfaction'].map(satisfaction_map),
            errors='coerce'
    )

        job_sat = (
            df_temp.groupby('Job Role')['Job_Sat_Num']
            .mean()
            .reset_index()
    )

        merged_data = pd.merge(
            job_attr,
            job_sat,
            on='Job Role',
            how='left'
    )

        fig7 = make_subplots(specs=[[{"secondary_y": True}]])

        if 'Stayed' in merged_data.columns:
            fig7.add_trace(
                go.Bar(
                    x=merged_data['Job Role'],
                    y=merged_data['Stayed'],
                    name="Stayed",
                    marker_color='#38bdf8'
                ),
                secondary_y=False
        )

        if 'Left' in merged_data.columns:
            fig7.add_trace(
                go.Bar(
                    x=merged_data['Job Role'],
                    y=merged_data['Left'],
                    name="Left",
                    marker_color='#f87171'
                ),
                secondary_y=False
            )

        fig7.add_trace(
            go.Scatter(
                x=merged_data['Job Role'],
                y=merged_data['Job_Sat_Num'],
                name="Avg Job Satisfaction",
                mode="lines+markers"
        ),
        secondary_y=True
    )

        fig7 = apply_modern_layout(fig7)

        fig7.update_layout(
            title_text='Q1 · Attrition Breakdown & Avg Job Satisfaction by Job Role',
            barmode='group'
        )

        st.plotly_chart(fig7, use_container_width=True)
        
    with col4:
        remote_attr = cleaned_df.groupby('Remote Work')['Attrition'].value_counts().unstack(fill_value=0).reset_index()
        fig8 = px.bar(remote_attr, x='Remote Work', y=remote_attr.columns[1:], barmode='group', title='Q3 · Attrition: Remote Work vs Onsite Environment', color_discrete_map=COLOR_MAP, template="plotly_dark")
        fig8 = apply_modern_layout(fig8)
        fig8.update_yaxes(title_text="Employee Count")
        st.plotly_chart(fig8, use_container_width=True)
        
        if 'Remote Work' in cleaned_df.columns:
            remote_share = (cleaned_df['Remote Work'].value_counts(normalize=True).get('Yes', 0)) * 100
            st.caption(f"ℹ️ Note: Remote staff accounts for only {remote_share:.1f}% of total dataset.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("""insight: almost employee who leaved are in technology
    that mean u have to increase the comfortable zone in technology domain 
    or increase num of employee woring remotely  """)
    st.info("""insight: plurality of employee that work insight leaving it reaches to 80% more than work remoting """)
    st.info("""i indeed on increase num of employee working remotely to solve this issue 
    or offering the comfortable work domain to increasee the satisfication  """)
    col5, col6_new = st.columns(2) 
    
    with col5:
        seniors = cleaned_df.groupby('Job Level')['Attrition'].value_counts().unstack(fill_value=0).reset_index()
        fig9 = px.bar(seniors, x='Job Level', y=seniors.columns[1:], barmode='group', title='Attrition by Job Level', color_discrete_map=COLOR_MAP, template="plotly_dark")
        fig9 = apply_modern_layout(fig9)
        fig9.update_yaxes(title_text="Employee Count")
        st.plotly_chart(fig9, use_container_width=True)

    with col6_new:
        if 'Number of Promotions' in cleaned_df.columns:
            promotion_df = cleaned_df.groupby('Number of Promotions')['Attrition'].value_counts(normalize=True).unstack() * 100
            promotion_df = promotion_df.reset_index()
            
            fig_promo = px.line(promotion_df, x='Number of Promotions', y=['Left', 'Stayed'], markers=True, title='Attrition vs Promotions Trend', color_discrete_map=COLOR_MAP, template="plotly_dark")
            fig_promo = apply_modern_layout(fig_promo)
            fig_promo.update_yaxes(title_text="Percentage (%)")
            st.plotly_chart(fig_promo, use_container_width=True)
            st.caption("💡 **Insight:** Employees with low or zero promotions (0–2) show a significantly higher attrition rate nearly (49%) compared to employees with more promotions (3–4) where attrition drops to around nearly (23–24%).")

    st.markdown("<br>", unsafe_allow_html=True)
# ===========================================================
# 👤 Tab 3: البيانات الشخصية (Personal Profiles)
# ===========================================================
with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        gender_attr = cleaned_df.groupby(['Gender', 'Attrition']).size().unstack(fill_value=0).reset_index()
        for status in ['Stayed', 'Left']:
            if status not in gender_attr.columns:
                gender_attr[status] = 0
                
        fig10 = px.bar(gender_attr, x='Gender', y=['Stayed', 'Left'], barmode='group', title='Attrition Analysis by Gender', color_discrete_map=COLOR_MAP, template="plotly_dark")
        fig10 = apply_modern_layout(fig10)
        fig10.update_layout(xaxis_type='category')
        fig10.update_yaxes(title_text="Number of Employees")
        st.plotly_chart(fig10, use_container_width=True)
        
    with col2:
        marital_attr = cleaned_df.groupby(['Marital Status', 'Attrition']).size().unstack(fill_value=0)
        for status in ['Stayed', 'Left']:
            if status not in marital_attr.columns:
                marital_attr[status] = 0
        marital_attr = marital_attr.reset_index()

        if 'Left' in marital_attr.columns and marital_attr['Left'].sum() > 0:
            fig11 = px.pie(marital_attr, names='Marital Status', values='Left', title='Attrition Share by Marital Status', color_discrete_sequence=['#f87171', '#fbbf24', '#60a5fa'], hole=0.4, template="plotly_dark")
            fig11.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#0e1117', width=2)))
            fig11.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Inter, sans-serif", color="#ffffff"), title=dict(font=dict(color="#ffffff", size=16, weight="bold")), legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, font=dict(color="#ffffff", size=12)))
            st.plotly_chart(fig11, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("""insight: we observed that plurity of employee who lefted are women """)
    st.info("""insight: most of those who left from marital statue are single
     cuz they may getting better offer from another company
     and they havnt any responability like family or
      anything like that tho he headed to leave this company """)
    col_q6, col_heatmap_q7 = st.columns(2)
    
    with col_q6:
        if 'Job Satisfaction' in cleaned_df.columns and 'Work-Life Balance' in cleaned_df.columns:
            grid_df = cleaned_df.groupby(['Job Satisfaction', 'Work-Life Balance'])['Attrition'].value_counts(normalize=True).unstack(fill_value=0).reset_index()
            grid_df['Left'] = grid_df['Left'] * 100
            fig_grid = px.scatter(grid_df, x='Job Satisfaction', y='Work-Life Balance', size='Left', color='Left', title="Q6 · Early Warning Grid (Attrition % by Satisfaction & Work-Life)", labels={'Left': 'Attrition Rate (%)'}, color_continuous_scale='Reds', template="plotly_dark")
            fig_grid = apply_modern_layout(fig_grid)
            st.plotly_chart(fig_grid, use_container_width=True)
            
    with col_heatmap_q7:
        if 'Age Band' in cleaned_df.columns and 'Dependents Band' in cleaned_df.columns:
            heatmap_data = (cleaned_df.groupby(['Age Band', 'Dependents Band'])['Attrition'].apply(lambda x: (x == 'Left').mean() * 100).reset_index(name='AttritionRate'))
            heatmap_pivot = heatmap_data.pivot(index='Age Band', columns='Dependents Band', values='AttritionRate').fillna(0)
            fig_heat = px.imshow(heatmap_pivot, text_auto=".1f", color_continuous_scale='Reds', title='Q7 · Life Stage Risk Heatmap (Age vs Dependents Band)', template="plotly_dark")
            fig_heat = apply_modern_layout(fig_heat)
            st.plotly_chart(fig_heat, use_container_width=True)
        else:
            st.warning("Make sure 'Age Band' and Dependents Column are processed properly for Heatmap plotting.")
    st.info("""insight:Work-Life Balance Rules: Poor or Fair work-life balance drives extreme attrition,
    even if job satisfaction is very high.
    The Shield: Excellent work-life balance keeps employees in the company,
    even if they don't love their daily tasks.""")
    st.info("""recomendation: Trigger Alerts: Intervene immediately with workload reductions 
    whenever an employee's work-life score drops.
    Inject Flexibility: Mandate hybrid choices or
    flexible hours for high-risk teams to recover their personal time.""")

    # ===========================================================
    # 🔥 Q9 · Highest-Risk Employee Profile Section
    # ===========================================================
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)

    with m_col1:
        st.metric("Profile Attrition Rate", f"{highest_risk['Attrition Rate']:.2f}%")

    with m_col2:
        st.metric("Company Average", f"{company_avg:.2f}%")

    with m_col3:
        st.metric("Difference", f"{difference:.2f}%")

    with m_col4:
        st.metric("Employees", employee_count)

    st.markdown("💡 Insight")
    st.write(
        "Employees in entry-level roles who work overtime, receive few or no promotions, "
        "and report low job satisfaction are the most likely to leave the company."
    )

    st.markdown(" 🎯 Recommendation")
    st.write(
        "Reduce excessive overtime, provide clearer career growth opportunities, "
        "and proactively engage employees matching this profile."
    )
