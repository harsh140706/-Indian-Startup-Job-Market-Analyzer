import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import ast

st.set_page_config(
    page_title="Indian Startup Job Market Analyzer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .insight-box {
        background: #fff8f0;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        border-left: 4px solid #e67e22;
        margin: 6px 0;
        font-size: 14px;
    }
    .fresher-box {
        background: #eafaf1;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        border-left: 4px solid #27ae60;
        margin: 6px 0;
        font-size: 14px;
    }
    .section-title {
        font-size: 17px;
        font-weight: 700;
        color: #ffffff;
        background-color: #2471a3;
        padding: 6px 12px;
        border-radius: 6px;
        margin: 1rem 0 0.6rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    df = pd.read_csv("data/jobs_cleaned.csv")
    def parse_skills(val):
        try:
            if isinstance(val, list):
                return val
            return ast.literal_eval(val)
        except:
            return []
    df['skills'] = df['skills'].apply(parse_skills)
    return df


df = load_data()

all_skills_global = []
for sl in df['skills']:
    all_skills_global.extend(sl)
skill_counts_global = pd.Series(all_skills_global).value_counts()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/combo-chart.png", width=55)
    st.title("Job Market Analyzer")
    st.caption("Indian Data Industry — 1,602 Real Listings")
    st.divider()
    st.subheader("🔧 Filters")

    exp_filter = st.multiselect(
        "Experience Level",
        options=['Fresher (0-2 yrs)', 'Mid-Level (3-5 yrs)', 'Senior (6+ yrs)'],
        default=['Fresher (0-2 yrs)', 'Mid-Level (3-5 yrs)', 'Senior (6+ yrs)']
    )
    sector_filter = st.multiselect(
        "Sector",
        options=sorted(df['sector'].dropna().unique().tolist()),
        default=sorted(df['sector'].dropna().unique().tolist())
    )
    salary_range = st.slider(
        "Avg Salary Range (LPA)",
        min_value=0.0,
        max_value=float(df['avg_salary'].max()),
        value=(0.0, float(df['avg_salary'].max()))
    )
    st.divider()
    st.caption("Built by Harsh Lal | KIIT 2023–27")
    st.caption("Data: Kaggle — Data Science Jobs India")

# ── Apply Filters ─────────────────────────────────────────────────────────────
filtered = df[
    (df['experience_category'].isin(exp_filter)) &
    (df['sector'].isin(sector_filter)) &
    (df['avg_salary'] >= salary_range[0]) &
    (df['avg_salary'] <= salary_range[1])
].copy()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🚀 Indian Startup Job Market Analyzer")
st.markdown(
    f"Analyzing **{len(filtered):,} job listings** from the Indian data industry — "
    f"helping freshers find the right role, skills, and salary to target."
)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Listings",   f"{len(filtered):,}")
k2.metric("Avg Salary",       f"₹{filtered['avg_salary'].mean():.1f} LPA")
k3.metric("Highest Salary",   f"₹{filtered['max_salary'].max():.0f} LPA")
k4.metric("Fresher Roles",    f"{len(filtered[filtered['experience_category']=='Fresher (0-2 yrs)']):,}")
k5.metric("Unique Companies", f"{filtered['company_name'].nunique():,}")

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", "🔧 Skills Analysis", "💰 Salary Insights",
    "🎓 Fresher Guide", "🔍 Explore Jobs"
])

# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═════════════════════════════════════════════════════════════════════════════
with tab1:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<p class="section-title">Jobs by Sector</p>', unsafe_allow_html=True)
        sc = filtered['sector'].value_counts().reset_index()
        sc.columns = ['Sector', 'Count']
        fig = px.pie(sc, values='Count', names='Sector', hole=0.5,
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_traces(textposition='outside', textinfo='percent+label')
        fig.update_layout(height=300, margin=dict(t=10,b=10), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<p class="section-title">Jobs by Experience Level</p>', unsafe_allow_html=True)
        exp_order = ['Fresher (0-2 yrs)', 'Mid-Level (3-5 yrs)', 'Senior (6+ yrs)']
        ec = filtered['experience_category'].value_counts().reindex(exp_order).reset_index()
        ec.columns = ['Level', 'Count']
        fig2 = px.bar(ec, x='Level', y='Count', color='Level',
                      color_discrete_map={
                          'Fresher (0-2 yrs)':'#27ae60',
                          'Mid-Level (3-5 yrs)':'#f39c12',
                          'Senior (6+ yrs)':'#e74c3c'},
                      text='Count')
        fig2.update_traces(textposition='outside')
        fig2.update_layout(height=300, margin=dict(t=10,b=10),
                            showlegend=False, xaxis_title='', yaxis_title='Listings')
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<p class="section-title">Average Salary by Job Title</p>', unsafe_allow_html=True)
    rs = filtered.groupby('job_title')['avg_salary'].mean().sort_values(ascending=False).reset_index()
    rs.columns = ['Role', 'Avg Salary (LPA)']
    fig3 = px.bar(rs, x='Role', y='Avg Salary (LPA)',
                  color='Role',
                  text=rs['Avg Salary (LPA)'].apply(lambda x: f'₹{x:.1f}L'),
                  color_discrete_sequence=px.colors.qualitative.Set1)
    fig3.update_traces(textposition='outside')
    fig3.update_layout(height=360, margin=dict(t=20,b=10),
                        showlegend=False, xaxis_tickangle=-30)
    st.plotly_chart(fig3, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — SKILLS ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
with tab2:
    f_skills = []
    for sl in filtered['skills']:
        f_skills.extend(sl)
    fsc = pd.Series(f_skills).value_counts().reset_index()
    fsc.columns = ['Skill', 'Count']
    fsc['% of Jobs'] = (fsc['Count'] / len(filtered) * 100).round(1)

    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown('<p class="section-title">Most In-Demand Skills</p>', unsafe_allow_html=True)
        top12 = fsc.head(12).copy()
        fig = px.bar(top12, x='Count', y='Skill', orientation='h',
                     color='Count',
                     color_continuous_scale=['#d6eaf8','#1a5276'],
                     text='Count')
        fig.update_traces(textposition='outside')
        fig.update_layout(height=420, margin=dict(t=10,b=10),
                           coloraxis_showscale=False,
                           yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<p class="section-title">Skill Coverage</p>', unsafe_allow_html=True)
        st.dataframe(fsc.head(15), use_container_width=True, height=420)

    st.markdown('<p class="section-title">Skills Required by Each Role</p>', unsafe_allow_html=True)
    role_skill_data = []
    for role, grp in filtered.groupby('job_title'):
        rs_skills = []
        for sl in grp['skills']:
            rs_skills.extend(sl)
        for skill, cnt in pd.Series(rs_skills).value_counts().head(5).items():
            role_skill_data.append({'Role': role, 'Skill': skill, 'Count': cnt})

    if role_skill_data:
        rs_df = pd.DataFrame(role_skill_data)
        fig_rs = px.bar(rs_df, x='Skill', y='Count', color='Skill',
                        facet_col='Role', facet_col_wrap=3,
                        color_discrete_sequence=px.colors.qualitative.Set2)
        fig_rs.update_layout(height=520, showlegend=False, margin=dict(t=40,b=10))
        fig_rs.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        st.plotly_chart(fig_rs, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 3 — SALARY INSIGHTS
# ═════════════════════════════════════════════════════════════════════════════
with tab3:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<p class="section-title">Salary by Experience Level</p>', unsafe_allow_html=True)
        exp_order = ['Fresher (0-2 yrs)', 'Mid-Level (3-5 yrs)', 'Senior (6+ yrs)']
        exp_sal = filtered.groupby('experience_category').agg(
            Avg=('avg_salary','mean'),
            Min=('min_salary','mean'),
            Max=('max_salary','mean')
        ).reindex(exp_order).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Min', x=exp_sal['experience_category'],
                              y=exp_sal['Min'], marker_color='#85c1e9'))
        fig.add_trace(go.Bar(name='Avg', x=exp_sal['experience_category'],
                              y=exp_sal['Avg'], marker_color='#2471a3'))
        fig.add_trace(go.Bar(name='Max', x=exp_sal['experience_category'],
                              y=exp_sal['Max'], marker_color='#1a2e5a'))
        fig.update_layout(barmode='group', height=320,
                           margin=dict(t=10,b=10), yaxis_title='Salary (LPA)',
                           xaxis_title='')
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<p class="section-title">Salary by Sector</p>', unsafe_allow_html=True)
        sec_sal = filtered.groupby('sector')['avg_salary'].mean().sort_values().reset_index()
        sec_sal.columns = ['Sector','Avg Salary']
        fig2 = px.bar(sec_sal, x='Avg Salary', y='Sector', orientation='h',
                      color='Avg Salary',
                      color_continuous_scale=['#d6eaf8','#1a5276'],
                      text=sec_sal['Avg Salary'].apply(lambda x: f'₹{x:.1f}L'))
        fig2.update_traces(textposition='outside')
        fig2.update_layout(height=320, margin=dict(t=10,b=10),
                            coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<p class="section-title">Salary Distribution by Role — Box Plot</p>',
                unsafe_allow_html=True)
    st.caption("The box shows the middle 50% of salaries. The line inside = median. Dots = outliers.")
    fig3 = px.box(filtered, x='job_title', y='avg_salary',
                   color='experience_category',
                   color_discrete_map={
                       'Fresher (0-2 yrs)':'#27ae60',
                       'Mid-Level (3-5 yrs)':'#f39c12',
                       'Senior (6+ yrs)':'#e74c3c'},
                   labels={'job_title':'Role','avg_salary':'Avg Salary (LPA)',
                            'experience_category':'Experience'})
    fig3.update_layout(height=420, margin=dict(t=10,b=10), xaxis_tickangle=-30)
    st.plotly_chart(fig3, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 4 — FRESHER GUIDE
# ═════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 🎓 If you are a fresher — here is exactly what to focus on")
    fresher_df = filtered[filtered['experience_category'] == 'Fresher (0-2 yrs)']

    f1, f2, f3, f4 = st.columns(4)
    f1.metric("Fresher Listings",   f"{len(fresher_df):,}")
    f2.metric("Avg Fresher Salary", f"₹{fresher_df['avg_salary'].mean():.1f} LPA")
    f3.metric("Max Fresher Salary", f"₹{fresher_df['max_salary'].max():.0f} LPA")
    f4.metric("Top Sector",
              fresher_df['sector'].value_counts().index[0] if len(fresher_df) > 0 else "N/A")

    st.divider()
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<p class="section-title">Fresher Openings by Role</p>', unsafe_allow_html=True)
        fr = fresher_df['job_title'].value_counts().reset_index()
        fr.columns = ['Role','Listings']
        fig = px.bar(fr, x='Listings', y='Role', orientation='h',
                     color='Listings',
                     color_continuous_scale=['#a9dfbf','#1e8449'],
                     text='Listings')
        fig.update_traces(textposition='outside')
        fig.update_layout(height=340, margin=dict(t=10,b=10),
                           coloraxis_showscale=False,
                           yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<p class="section-title">Fresher Salary by Role</p>', unsafe_allow_html=True)
        fs = fresher_df.groupby('job_title')['avg_salary'].mean().sort_values().reset_index()
        fs.columns = ['Role','Avg Salary']
        fig2 = px.bar(fs, x='Avg Salary', y='Role', orientation='h',
                      color='Avg Salary',
                      color_continuous_scale=['#a9dfbf','#1e8449'],
                      text=fs['Avg Salary'].apply(lambda x: f'₹{x:.1f}L'))
        fig2.update_traces(textposition='outside')
        fig2.update_layout(height=340, margin=dict(t=10,b=10),
                            coloraxis_showscale=False,
                            yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.markdown("### 📌 Your Personal Action Plan")

    if len(fresher_df) > 0:
        top_role   = fresher_df['job_title'].value_counts().index[0]
        top_sal_role = fresher_df.groupby('job_title')['avg_salary'].mean().idxmax()
        top_sal    = fresher_df.groupby('job_title')['avg_salary'].mean().max()
        fsk_flat   = []
        for sl in fresher_df['skills']:
            fsk_flat.extend(sl)
        top3 = pd.Series(fsk_flat).value_counts().head(3).index.tolist()

        actions = [
            (f"Most openings: {top_role}",
             f"This role has the highest number of fresher listings. "
             f"Highest chance of getting a callback — start here."),
            (f"Best paying fresher role: {top_sal_role} @ ₹{top_sal:.1f} LPA avg",
             f"If salary is your priority, target this role. "
             f"Build the required skills and apply aggressively."),
            (f"Top 3 skills to learn right now: {', '.join(top3)}",
             f"These appear most in fresher listings. "
             f"Learn them in this order — don't jump around."),
            ("Build and deploy one project",
             "Freshers with a live deployed project get far more callbacks. "
             "A Streamlit dashboard or GitHub repo makes your resume stand out immediately."),
            ("Target FinTech and Analytics sectors first",
             "These sectors have the most fresher openings AND the best salary bands "
             "for entry-level roles in the Indian startup ecosystem."),
        ]

        for title, desc in actions:
            st.markdown(f"""
            <div class="fresher-box">
                <b>{title}</b><br>{desc}
            </div>
            """, unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 5 — EXPLORE JOBS
# ═════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<p class="section-title">Search All Listings</p>', unsafe_allow_html=True)

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        role_sel = st.selectbox("Filter by Role",
                                ['All'] + sorted(filtered['job_title'].unique().tolist()))
    with sc2:
        company_search = st.text_input("Search Company", "")
    with sc3:
        sort_col = st.selectbox("Sort By",
                                ['avg_salary','min_salary','max_salary','min_experience'])

    display = filtered.copy()
    if role_sel != 'All':
        display = display[display['job_title'] == role_sel]
    if company_search:
        display = display[display['company_name'].str.contains(
            company_search, case=False, na=False)]
    display = display.sort_values(sort_col, ascending=False)

    display['skills_str'] = display['skills'].apply(
        lambda x: ', '.join(x) if isinstance(x, list) else x)
    display['salary'] = display.apply(
        lambda r: f"₹{r['min_salary']:.0f}L – ₹{r['max_salary']:.0f}L (avg ₹{r['avg_salary']:.1f}L)",
        axis=1)

    st.caption(f"Showing {len(display):,} listings")
    st.dataframe(
        display[['job_title','company_name','sector','salary',
                 'min_experience','experience_category','skills_str']].rename(columns={
            'job_title':'Role', 'company_name':'Company', 'sector':'Sector',
            'salary':'Salary', 'min_experience':'Min Exp (yrs)',
            'experience_category':'Level', 'skills_str':'Skills'
        }),
        use_container_width=True, height=460
    )

    csv = display.drop(columns=['skills','skills_str']).to_csv(index=False).encode()
    st.download_button("⬇ Download CSV", csv, "filtered_jobs.csv", "text/csv")