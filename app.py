"""Streamlit interface for research proposal pre-submission self-review."""

from __future__ import annotations

import streamlit as st

from review_engine import ProposalInput, ProposalReview, build_report, priority_actions, review_proposal


st.set_page_config(
    page_title="Research Proposal Self-Review",
    page_icon="🧭",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root {
        --teal: #20575b;
        --teal-dark: #153f43;
        --orange: #ef6c00;
        --paper: #f7f4ee;
    }
    .stApp { background: linear-gradient(180deg, #f7f4ee 0%, #ffffff 38%); }
    .hero {
        padding: 1.55rem 1.7rem;
        border-radius: 18px;
        background: linear-gradient(125deg, var(--teal-dark), var(--teal));
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 10px 28px rgba(21,63,67,.16);
    }
    .hero h1 { margin: 0 0 .35rem 0; color: white; font-size: 2.15rem; }
    .hero p { margin: 0; color: #e9f3f2; font-size: 1.03rem; }
    .eyebrow { color: #ffad5c; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #dce6e3;
        padding: .8rem 1rem;
        border-radius: 12px;
    }
    .stButton > button[kind="primary"] {
        background: var(--orange);
        border-color: var(--orange);
        font-weight: 700;
    }
    .small-note { color: #536061; font-size: .91rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_section(review_section) -> None:
    st.progress(review_section.score / 100)
    for item in review_section.criteria:
        icon = "✓" if item.passed else "↻"
        status = "Meets check" if item.passed else "Review"
        st.markdown(f"**{icon} {item.title} · {status}**")
        st.caption(item.feedback)


def render_results(data: ProposalInput, review: ProposalReview) -> None:
    st.divider()
    st.markdown("## Proposal readiness review")
    overall_col, status_col = st.columns([1, 2])
    with overall_col:
        st.metric("Overall readiness indicator", f"{review.overall_score}/100")
    with status_col:
        st.metric("Current status", review.label)
    st.progress(review.overall_score / 100)
    st.caption(
        "This indicator prioritises coverage and alignment. It is not an official evaluation score, and the approximate length checks are not official word limits."
    )

    st.markdown("### Priority revision actions")
    priorities = priority_actions(review)
    if priorities:
        for number, (section, feedback, _impact) in enumerate(priorities, start=1):
            st.write(f"{number}. **{section}:** {feedback}")
    else:
        st.success("All automated checks are met. Complete the final human checks before submission.")

    st.markdown("### Section overview")
    columns = st.columns(3)
    for index, section in enumerate(review.sections):
        with columns[index % 3]:
            st.metric(section.name, f"{section.score}/100")

    st.markdown("### Detailed feedback")
    for section in review.sections:
        with st.expander(f"{section.name} · {section.score}/100 · {section.label}"):
            render_section(section)

    st.markdown("### Final human checks")
    left, right = st.columns(2)
    with left:
        st.checkbox("An evaluator can quickly identify what, why and how.", key="human_what_why_how")
        st.checkbox("Every research question maps to an objective and method.", key="human_alignment")
        st.checkbox("Claims about previous research are supported by sources.", key="human_claims")
    with right:
        st.checkbox("Expected results are not presented as predetermined findings.", key="human_expected")
        st.checkbox("In-text citations and references have been cross-checked.", key="human_refs")
        st.checkbox("The required format, limits and submission instructions are met.", key="human_format")

    report = build_report(data, review)
    st.download_button(
        "Download my self-review report",
        data=report,
        file_name="research_proposal_self_review.txt",
        mime="text/plain",
        use_container_width=True,
    )


st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Pre-submission formative review</div>
      <h1>Research Proposal Self-Review</h1>
      <p>Check whether your proposal gives evaluators sufficient evidence to judge what you will study, why it is worthwhile and how you will carry it out.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("How to use this reviewer", expanded=False):
    st.markdown(
        """
        Paste the current draft of each proposal section. The app applies transparent language and alignment checks based on the supplied research proposal guidance. Review the feedback, revise your proposal, and run it again. Your text is processed only in the active app session and is not sent to an AI service.

        The reviewer cannot verify whether a research gap is true, whether a method is academically appropriate, or whether references are accurate. Those decisions still require your judgement, source checking and evaluator guidance.
        """
    )

write_tab, guide_tab, structure_tab = st.tabs(["Enter proposal", "Review guide", "Suggested structure"])

with write_tab:
    with st.form("proposal_form"):
        st.markdown("### Proposal details")
        title = st.text_input(
            "Working title",
            placeholder="Enter a specific title that reflects the proposed inquiry",
        )

        with st.expander("1 · Introduction", expanded=True):
            st.caption("Introduce the topic area and context, identify the problem or gap, and explain its significance to knowledge or practice.")
            introduction = st.text_area(
                "Introduction",
                height=230,
                placeholder="Provide the frame of reference, topic context, problem or gap, and significance …",
            )

        with st.expander("2 · Research questions", expanded=True):
            st.caption("State all research questions or hypotheses fully in one place. Enter one per line.")
            research_questions = st.text_area(
                "Research questions or hypotheses",
                height=150,
                placeholder="1. How does …?\n2. To what extent does …?",
            )

        with st.expander("3 · Objectives", expanded=True):
            st.caption("Give a concise, clear outline of what the project intends to find out or achieve. Enter one objective per line.")
            objectives = st.text_area(
                "Research objectives",
                height=150,
                placeholder="1. To examine …\n2. To evaluate …",
            )

        with st.expander("4 · Brief literature review", expanded=False):
            st.caption("Synthesize previous research, key achievements and references; show how the proposal builds on earlier work and opens a new line of inquiry.")
            literature_review = st.text_area(
                "Brief literature review",
                height=320,
                placeholder="Summarise and connect the main research, then establish how your proposal builds on it …",
            )
            preliminary_work_not_applicable = st.checkbox(
                "There is no relevant preliminary or earlier work by the applicant/team to report."
            )

        with st.expander("5 · Methodology and theoretical framework", expanded=False):
            st.caption("Describe the approach, research design, data needs, methods, procedures, analytic techniques and plan for interpreting results.")
            methodology = st.text_area(
                "Methodology and theoretical or conceptual framework",
                height=340,
                placeholder="State and justify the design; identify the data source, collection procedures, analysis and interpretation plan …",
            )
            framework_not_applicable = st.checkbox(
                "A theoretical or conceptual framework is not applicable to this study."
            )

        with st.expander("6 · Expected results and significance", expanded=False):
            st.caption("Describe plausible expected findings and how they may support conclusions or contribute to knowledge or practice.")
            expected_results = st.text_area(
                "Expected results and significance",
                height=210,
                placeholder="The study is expected to … These findings may contribute by …",
            )

        with st.expander("7 · Feasibility and work plan", expanded=False):
            st.caption("Show that the project can be completed through a workable sequence, milestones and realistic access to people or resources.")
            work_plan = st.text_area(
                "Feasibility and work plan",
                height=210,
                placeholder="Phase 1 … Month 1 … Required access and resources … Key risk and mitigation …",
            )

        with st.expander("8 · References", expanded=False):
            st.caption("Paste one complete reference per line. Include every source cited in the proposal.")
            references = st.text_area(
                "Reference list",
                height=250,
                placeholder="Author, A. A. (Year). Title. Source.\nAuthor, B. B. (Year). Title. Source.",
            )

        submitted = st.form_submit_button(
            "Review my proposal",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        data = ProposalInput(
            title=title,
            introduction=introduction,
            research_questions=research_questions,
            objectives=objectives,
            literature_review=literature_review,
            methodology=methodology,
            expected_results=expected_results,
            work_plan=work_plan,
            references=references,
            preliminary_work_not_applicable=preliminary_work_not_applicable,
            framework_not_applicable=framework_not_applicable,
        )
        substantive_text = " ".join(
            [
                introduction,
                research_questions,
                objectives,
                literature_review,
                methodology,
                expected_results,
                work_plan,
            ]
        )
        if not substantive_text.strip():
            st.error("Enter at least one proposal section before starting the review.")
        else:
            st.session_state["proposal_review_data"] = data
            st.session_state["proposal_review_result"] = review_proposal(data)

    if "proposal_review_result" in st.session_state:
        render_results(
            st.session_state["proposal_review_data"],
            st.session_state["proposal_review_result"],
        )

with guide_tab:
    st.markdown("## What evaluators need to see")
    st.markdown(
        """
        The proposal should provide enough information for a reader to evaluate whether the project is worthwhile and whether the applicant has a credible plan to complete it.

        | Proposal element | Evidence to include |
        |---|---|
        | **Introduction** | Topic area, frame of reference, fully stated questions, and significance to knowledge or practice |
        | **Brief literature review** | Previous research, key references, relevant preliminary work, and how the proposed study builds on earlier work |
        | **Methodology or framework** | Approach, research design, data needs, procedures, analytic techniques, interpretation plan and expected results |
        | **Objectives** | A concise, clear account of what the project will find out or achieve and why it is valuable |
        | **Work plan** | A realistic sequence, milestones, access and resources showing the project can be completed |
        | **References** | A complete list of all sources cited in the proposal |
        """
    )
    st.info(
        "Use the readiness indicator to find missing evidence. Do not treat it as a predicted evaluation result: reviewers will also judge disciplinary quality, originality, feasibility and accuracy."
    )

with structure_tab:
    st.markdown("## Suggested drafting sequence")
    st.markdown(
        """
        1. **Context:** Establish the topic area and the issue that makes the study necessary.
        2. **Gap and significance:** Explain what is not yet known or addressed and why it matters.
        3. **Research questions:** State the inquiry fully in one place.
        4. **Objectives:** Translate each question into a precise action and intended outcome.
        5. **Literature synthesis:** Show what earlier studies established and how the proposal builds on them.
        6. **Methodology:** Explain the design, data, procedures, analysis and interpretation needed to answer each question.
        7. **Expected contribution:** Describe plausible results cautiously and explain their value.
        8. **Work plan and references:** Demonstrate feasibility and verify that every citation is listed.
        """
    )
    st.markdown("### Alignment prompts")
    st.markdown(
        """
        - For every research question, which objective addresses it?
        - What data will provide the evidence needed for that question?
        - Which analytic technique will turn that data into an answer?
        - Which part of the literature establishes the need for that question?
        - What expected contribution would justify carrying out the study?
        """
    )

st.divider()
st.markdown(
    '<p class="small-note">Formative self-review only. Automated checks may miss valid disciplinary wording and cannot verify the truth of a research gap, the suitability of a method or the accuracy of references.</p>',
    unsafe_allow_html=True,
)
