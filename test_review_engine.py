import unittest

from review_engine import ProposalInput, review_proposal


def strong_proposal() -> ProposalInput:
    return ProposalInput(
        title="Lecturer use of learning analytics for targeted instructional support",
        introduction=(
            "Learning analytics dashboards are increasingly used in polytechnic education to help lecturers "
            "understand students' engagement and performance. Previous research has reported potential benefits, "
            "but limited evidence explains how lecturers use dashboard information for targeted instructional "
            "support in applied learning contexts. This knowledge gap is important because access to data does not "
            "automatically improve teaching decisions. The study may contribute practical knowledge about the "
            "conditions that support meaningful instructional use."
        ),
        research_questions=(
            "How do polytechnic lecturers use learning analytics dashboards for targeted instructional support?\n"
            "What factors influence lecturers' use of dashboard information in teaching decisions?"
        ),
        objectives=(
            "To examine how polytechnic lecturers use learning analytics dashboards for targeted instructional support.\n"
            "To identify factors that influence lecturers' use of dashboard information in teaching decisions."
        ),
        literature_review=(
            "Previous research has examined learning analytics adoption and dashboard use in higher education. "
            "Smith (2022) found that accessible visualisations can support interpretation, while Tan and Lee (2023) "
            "reported that lecturers require contextual guidance. Existing literature also shows that perceived "
            "usefulness influences adoption (Koh, 2024). However, limited research has explained how dashboard "
            "information becomes targeted instructional support in applied polytechnic contexts. The proposed study "
            "builds on these adoption studies by extending the inquiry from access and perceptions to lecturers' "
            "teaching decisions. A preliminary pilot by the research team indicated variation in how lecturers used "
            "class and question-level analytics. This line of inquiry directly supports the research questions about "
            "instructional use and influencing factors."
        ),
        methodology=(
            "The study will use a sequential explanatory mixed-methods research design because the questions require "
            "both patterns of dashboard use and explanations of teaching decisions. The population comprises "
            "polytechnic lecturers who have accessed the dashboard, from whom a purposive sample will be recruited. "
            "Survey data will first be collected through a questionnaire measuring use, perceived usefulness and "
            "instructional application. Descriptive statistics and correlation analysis will identify overall patterns "
            "and relationships. Follow-up focus group interviews will then explore how lecturers interpret analytics "
            "and apply them to targeted support. Qualitative data will be analysed through thematic coding. Findings "
            "from both phases will be integrated and interpreted against the technology acceptance model and prior "
            "literature. Triangulation across survey and interview evidence will support credible conclusions."
        ),
        expected_results=(
            "The study is expected to identify different patterns of dashboard use and factors that may support or "
            "constrain targeted instructional decisions. The findings may contribute knowledge about how adoption "
            "conditions shape teaching practice and provide practical implications for dashboard design and staff development."
        ),
        work_plan=(
            "Phase 1 will finalise instruments and permissions in Month 1. Participant recruitment and survey data "
            "collection will take place in Months 2 and 3, followed by analysis and focus groups in Months 4 and 5. "
            "The team has access to the dashboard user population and the required survey software. The main risk is "
            "low recruitment; reminders and additional focus-group dates will keep the scope feasible."
        ),
        references=(
            "Koh, A. (2024). Learning analytics adoption in higher education. Journal of Learning Analytics.\n"
            "Smith, B. (2022). Visual analytics and lecturer decision making. Educational Technology Research.\n"
            "Tan, C., & Lee, D. (2023). Supporting lecturers' interpretation of dashboard data. Higher Education Studies."
        ),
    )


class ProposalReviewTests(unittest.TestCase):
    def test_strong_proposal_scores_as_ready(self):
        review = review_proposal(strong_proposal())
        self.assertGreaterEqual(review.overall_score, 80)

    def test_empty_proposal_is_low(self):
        data = ProposalInput("", "", "", "", "", "", "", "", "")
        review = review_proposal(data)
        self.assertLess(review.overall_score, 20)

    def test_alignment_flags_disconnected_questions_and_objectives(self):
        data = strong_proposal()
        disconnected = ProposalInput(
            **{**data.__dict__, "objectives": "To evaluate coastal erosion using satellite imagery."}
        )
        review = review_proposal(disconnected)
        alignment = next(section for section in review.sections if section.name == "Overall alignment")
        criterion = next(
            item for item in alignment.criteria if item.title == "Research questions and objectives align"
        )
        self.assertFalse(criterion.passed)

    def test_missing_method_details_are_flagged(self):
        data = strong_proposal()
        weak = ProposalInput(**{**data.__dict__, "methodology": "A study will be conducted."})
        review = review_proposal(weak)
        method = next(
            section for section in review.sections if section.name == "Methodology and theoretical framework"
        )
        self.assertLess(method.score, 40)

    def test_unmatched_citations_are_flagged(self):
        data = strong_proposal()
        weak = ProposalInput(**{**data.__dict__, "references": "Different, A. (2020). Unrelated source. Journal."})
        review = review_proposal(weak)
        references = next(section for section in review.sections if section.name == "References")
        criterion = next(item for item in references.criteria if item.title == "Citations appear in the reference list")
        self.assertFalse(criterion.passed)


if __name__ == "__main__":
    unittest.main()
