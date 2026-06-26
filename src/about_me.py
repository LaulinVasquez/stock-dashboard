import streamlit as st
import streamlit.components.v1 as components


def show_about_page():
    with st.sidebar:
        st.header("🧭 Explore")
        st.radio("Navigate", ["Dashboard", "About me"], key="page_nav")
        st.caption("Switch between the live dashboard and my profile.")

    if st.session_state.get("page_nav") == "Dashboard":
        from src.stock_dashboard import render_dashboard

        render_dashboard()
        return
    st.markdown(
        """
        <style>
        .hero {
            background: linear-gradient(135deg, rgba(79,140,255,0.22), rgba(255,255,255,0.06));
            border: 1px solid rgba(255,255,255,0.16);
            border-radius: 24px;
            padding: 1.3rem 1.4rem;
            box-shadow: 0 12px 32px rgba(0,0,0,0.22);
            margin-bottom: 1rem;
        }
        .skill-pill {
            display: inline-block;
            margin: 0.25rem 0.35rem 0.25rem 0;
            padding: 0.45rem 0.7rem;
            border-radius: 999px;
            background: rgba(79,140,255,0.16);
            border: 1px solid rgba(255,255,255,0.12);
            color: white;
            animation: pulse 2.2s infinite;
        }
        @keyframes pulse {
            0%, 100% { transform: translateY(0px); box-shadow: 0 0 0 rgba(79,140,255,0); }
            50% { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(79,140,255,0.25); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.title("👋 Laurin Vasquez")
    st.subheader("Software engineering student • data-driven builder • thoughtful problem solver")
    st.write(
        "I enjoy crafting polished digital products that blend reliable engineering, meaningful analytics, and clean design."
    )
    st.markdown('</div>', unsafe_allow_html=True)

    hero_cols = st.columns([1.2, 0.8])
    with hero_cols[0]:
        st.markdown("### About me")
        st.write(
            "I’m a software engineering student with experience in software development, analytics, leadership, and operations management."
        )
        st.write(
            "My work focuses on turning data into clear decisions, building polished web apps, and creating tools that feel simple and powerful."
        )
    with hero_cols[1]:
        st.markdown("### Quick highlights")
        st.metric("Focus", "Product + Data")
        st.metric("Style", "Clean + Interactive")
        st.metric("Goal", "Make information feel alive")

    st.markdown("### Core skills")
    html = """
    <div id='skill-rotator' style='margin-top:10px; padding:12px; border-radius:16px; background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.12);'></div>
    <script>
    const skills = ['Python', 'C#', 'JavaScript', 'TypeScript', 'React', 'Node.js', 'SQL', 'Power BI', 'Excel', 'Data Analysis', 'Leadership', 'Visualization'];
    const rotator = document.getElementById('skill-rotator');
    let index = 0;
    function renderSkill() {
      rotator.innerHTML = skills.map((skill, i) => '<span class="skill-pill" style="background:' + (i === index ? 'rgba(79,140,255,0.35)' : 'rgba(79,140,255,0.16)') + '">' + skill + '</span>').join('');
      index = (index + 1) % skills.length;
    }
    renderSkill();
    setInterval(renderSkill, 1400);
    </script>
    """
    components.html(f"<style>.skill-pill {{ display:inline-block; margin:0.2rem 0.35rem 0.2rem 0; padding:0.45rem 0.7rem; border-radius:999px; border:1px solid rgba(255,255,255,0.12); color:white; }} </style>{html}", height=140)

    st.markdown("### Experience snapshot")
    exp_cols = st.columns(3)
    with exp_cols[0]:
        st.info("Assistant Manager • Data Analytics Specialist")
        st.caption("Built dashboards, analyzed operations data, and trained teams.")
    with exp_cols[1]:
        st.info("Assistant Manager • Logistics Specialist")
        st.caption("Managed workflows, schedules, and staffing for large teams.")
    with exp_cols[2]:
        st.info("Collections Specialist")
        st.caption("Worked with CRM systems, SQL reporting, and business insights.")

    st.markdown("### Education")
    st.write("Brigham Young University – Idaho")
    st.caption("Bachelor of Software Engineering • GPA 3.89")

    st.markdown("### A little more personality")
    st.write("This dashboard is one example of the style I like to build: useful, elegant, and easy to explore.")

    st.markdown("---")
    st.caption("Built with care by Laurin Vasquez")


if __name__ == "__main__":
    show_about_page()
