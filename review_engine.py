"""Transparent formative checks for research proposal self-review.

The checks operationalise the supplied SP research proposal guidance. They are
prompts for revision, not an institutional evaluation rubric or a substitute
for disciplinary judgement.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable


@dataclass(frozen=True)
class Criterion:
    title: str
    passed: bool
    feedback: str
    weight: int


@dataclass(frozen=True)
class SectionReview:
    name: str
    score: int
    label: str
    criteria: tuple[Criterion, ...]


@dataclass(frozen=True)
class ProposalReview:
    overall_score: int
    label: str
    sections: tuple[SectionReview, ...]


@dataclass(frozen=True)
class ProposalInput:
    title: str
    introduction: str
    research_questions: str
    objectives: str
    literature_review: str
    methodology: str
    expected_results: str
    work_plan: str
    references: str
    preliminary_work_not_applicable: bool = False
    framework_not_applicable: bool = False


SECTION_WEIGHTS = {
    "Introduction": 15,
    "Research questions": 10,
    "Objectives": 10,
    "Brief literature review": 20,
    "Methodology and theoretical framework": 25,
    "Expected results and significance": 5,
    "Feasibility and work plan": 5,
    "References": 5,
    "Overall alignment": 5,
}


STOPWORDS = {
    "a", "about", "after", "against", "all", "also", "an", "and", "are", "as", "at",
    "be", "because", "been", "before", "being", "between", "both", "but", "by", "can",
    "could", "data", "do", "does", "for", "from", "further", "has", "have", "how", "in",
    "into", "is", "it", "its", "may", "method", "methods", "more", "most", "not", "objective",
    "objectives", "of", "on", "or", "our", "proposal", "question", "questions", "research",
    "results", "should", "study", "than", "that", "the", "their", "there", "these", "this",
    "to", "using", "was", "we", "were", "what", "when", "which", "while", "who", "why",
    "will", "with", "within", "would",
}


GAP_PATTERNS = (
    r"\bresearch gap\b",
    r"\black of\b",
    r"\blimited (?:evidence|knowledge|research|understanding|work|attention)\b",
    r"\bhas not been\b",
    r"\bhave not been\b",
    r"\bnot yet\b",
    r"\bremains? (?:unclear|unknown|unexplored|underexplored|unaddressed)\b",
    r"\bunder[- ]?researched\b",
    r"\bfew studies\b",
    r"\bhowever\b",
    r"\bdespite\b",
)

SIGNIFICANCE_PATTERNS = (
    r"\bsignifican",
    r"\bimportant\b",
    r"\bcontribut",
    r"\bvalue\b",
    r"\bknowledge\b",
    r"\bimplication",
    r"\bbenefit",
    r"\bimpact",
    r"\bthis matters\b",
    r"\baddress(?:es|ing)? the (?:problem|gap|need)\b",
)

ACTION_PATTERNS = (
    r"\banalys(?:e|es|ed|ing)\b",
    r"\bassess(?:es|ed|ing)?\b",
    r"\bcompar(?:e|es|ed|ing)\b",
    r"\bdetermin(?:e|es|ed|ing)\b",
    r"\bdevelop(?:s|ed|ing)?\b",
    r"\bevaluat(?:e|es|ed|ing)\b",
    r"\bexamin(?:e|es|ed|ing)\b",
    r"\bexplor(?:e|es|ed|ing)\b",
    r"\bidentif(?:y|ies|ied|ying)\b",
    r"\binvestigat(?:e|es|ed|ing)\b",
    r"\bmeasur(?:e|es|ed|ing)\b",
    r"\btest(?:s|ed|ing)?\b",
    r"\bunderstand(?:s|ing)?\b",
)

DESIGN_PATTERNS = (
    r"\b(?:qualitative|quantitative|mixed[- ]methods?)\b",
    r"\b(?:experimental|quasi-experimental|descriptive|correlational|exploratory) design\b",
    r"\bcase stud(?:y|ies)\b",
    r"\baction research\b",
    r"\bsurvey design\b",
    r"\bresearch design\b",
    r"\bapproach\b",
)

DATA_SOURCE_PATTERNS = (
    r"\bparticipants?\b",
    r"\bsample\b",
    r"\bpopulation\b",
    r"\brespondents?\b",
    r"\bstudents?\b",
    r"\bstaff\b",
    r"\bdocuments?\b",
    r"\bdataset\b",
    r"\bdata source",
)

COLLECTION_PATTERNS = (
    r"\bcollect",
    r"\bsurvey\b",
    r"\bquestionnaire\b",
    r"\binterviews?\b",
    r"\bfocus groups?\b",
    r"\bobservation",
    r"\bassessment (?:scores|results|data)\b",
    r"\bdocument analysis\b",
    r"\bprocedure",
)

ANALYSIS_PATTERNS = (
    r"\banalys",
    r"\bthematic\b",
    r"\bcontent analysis\b",
    r"\bdescriptive statistics\b",
    r"\binferential\b",
    r"\bt[- ]?test\b",
    r"\banova\b",
    r"\bregression\b",
    r"\bcorrelation\b",
    r"\bcoding\b",
)

INTERPRETATION_PATTERNS = (
    r"\binterpret",
    r"\btriangulat",
    r"\bvalidit",
    r"\breliabilit",
    r"\bcredibilit",
    r"\bcompare.*(?:literature|framework|theory)\b",
    r"\bconclusion",
)

FRAMEWORK_PATTERNS = (
    r"\btheoretical framework\b",
    r"\bconceptual framework\b",
    r"\btheor(?:y|ies|etical)\b",
    r"\bmodel\b",
    r"\blens\b",
)


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def _contains_any(text: str, patterns: Iterable[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL) for pattern in patterns)


def extract_keywords(text: str) -> set[str]:
    words = re.findall(r"\b[a-z][a-z0-9-]{2,}\b", text.lower())
    return {word for word in words if word not in STOPWORDS}


def _shared_keywords(first: str, second: str) -> list[str]:
    return sorted(extract_keywords(first) & extract_keywords(second))


def _items(text: str, *, questions: bool = False) -> list[str]:
    raw = text.strip()
    if not raw:
        return []
    lines = [
        re.sub(r"^\s*(?:[-•*]|\(?\d+[.)]|[A-Za-z][.)])\s*", "", line).strip()
        for line in raw.splitlines()
        if line.strip()
    ]
    if len(lines) == 1 and questions and raw.count("?") > 1:
        lines = [part.strip() for part in re.findall(r"[^?]+\?", raw) if part.strip()]
    if len(lines) == 1 and not questions and raw.count(";") >= 1:
        lines = [part.strip() for part in raw.split(";") if part.strip()]
    return lines


def _label(score: int) -> str:
    if score >= 85:
        return "Ready for final human review"
    if score >= 70:
        return "Strong foundation; revise selected areas"
    if score >= 50:
        return "Developing; substantive revision needed"
    return "Incomplete or insufficiently evidenced"


def _section(name: str, criteria: list[Criterion]) -> SectionReview:
    score = sum(item.weight for item in criteria if item.passed)
    return SectionReview(name=name, score=score, label=_label(score), criteria=tuple(criteria))


def review_introduction(data: ProposalInput) -> SectionReview:
    text = _normalise(data.introduction)
    words = _word_count(text)
    keywords = extract_keywords(text)
    criteria = [
        Criterion(
            "Provides sufficient orientation",
            words >= 50,
            f"The introduction contains {words} words. This is only a coverage prompt—not an official word limit. Add enough context for a reviewer unfamiliar with the topic."
            if words < 50 else "The introduction provides enough material for the remaining checks to be meaningful.",
            15,
        ),
        Criterion(
            "Defines the topic area and context",
            len(keywords) >= 12,
            "Name the topic, field or setting and provide a frame of reference or necessary definition."
            if len(keywords) < 12 else "The topic area and context appear sufficiently specific.",
            20,
        ),
        Criterion(
            "Identifies the problem or knowledge gap",
            _contains_any(text, GAP_PATTERNS),
            "State what is missing, unresolved or insufficient in existing knowledge or practice."
            if not _contains_any(text, GAP_PATTERNS) else "The introduction signals a problem or gap that warrants investigation.",
            25,
        ),
        Criterion(
            "Explains significance to knowledge or practice",
            _contains_any(text, SIGNIFICANCE_PATTERNS),
            "Explain why the topic matters and what knowledge or practice may benefit."
            if not _contains_any(text, SIGNIFICANCE_PATTERNS) else "The introduction explains why the proposed study is worthwhile.",
            25,
        ),
        Criterion(
            "Leads to fully stated research questions",
            bool(data.research_questions.strip()),
            "State all research questions together in the research-question section."
            if not data.research_questions.strip() else "A dedicated research-question section follows the introduction.",
            15,
        ),
    ]
    return _section("Introduction", criteria)


def review_research_questions(data: ProposalInput) -> SectionReview:
    questions = _items(data.research_questions, questions=True)
    combined = " ".join(questions)
    shared = _shared_keywords(combined, data.objectives)
    complete_form = bool(questions) and all(
        item.rstrip().endswith("?") or re.search(r"\bhypothes(?:is|ise|ized|ised)\b", item, re.I)
        for item in questions
    )
    researchable = _contains_any(
        combined,
        (*ACTION_PATTERNS, r"\bhow\b", r"\bwhat\b", r"\bto what extent\b", r"\brelationship\b", r"\bdifference\b", r"\beffect\b", r"\bexperience", r"\bperception"),
    )
    criteria = [
        Criterion(
            "Questions are fully stated in one place",
            bool(questions) and complete_form,
            "Write each research question in full and place all questions together; use a question mark or state a testable hypothesis clearly."
            if not complete_form else "The research questions or hypotheses are fully stated together.",
            25,
        ),
        Criterion(
            "Scope is manageable",
            1 <= len(questions) <= 4,
            f"The reviewer detected {len(questions)} item(s). A focused proposal usually needs one to four main questions; check your programme's requirements."
            if not 1 <= len(questions) <= 4 else f"The proposal has {len(questions)} focused research question(s).",
            15,
        ),
        Criterion(
            "Questions are researchable",
            researchable,
            "Ask about an examinable relationship, effect, experience, process, difference or phenomenon rather than a broad topic."
            if not researchable else "The wording indicates an inquiry that can be investigated.",
            25,
        ),
        Criterion(
            "Questions are sufficiently specific",
            len(extract_keywords(combined)) >= 6,
            "Specify the phenomenon or variables and, where relevant, the participants, setting or context."
            if len(extract_keywords(combined)) < 6 else "The questions contain a specific focus and context.",
            15,
        ),
        Criterion(
            "Questions align with objectives",
            len(shared) >= 2,
            "Use consistent key concepts across the research questions and objectives."
            if len(shared) < 2 else "Shared concepts include: " + ", ".join(shared[:6]) + ".",
            20,
        ),
    ]
    return _section("Research questions", criteria)


def review_objectives(data: ProposalInput) -> SectionReview:
    objectives = _items(data.objectives)
    combined = " ".join(objectives)
    shared = _shared_keywords(combined, data.research_questions)
    lengths = [_word_count(item) for item in objectives]
    criteria = [
        Criterion(
            "Objectives are concise and clearly separated",
            1 <= len(objectives) <= 5 and all(5 <= length <= 40 for length in lengths),
            "List one to five objectives separately. Keep each focused on one main outcome; the length check is a readability prompt, not an official limit."
            if not (1 <= len(objectives) <= 5 and all(5 <= length <= 40 for length in lengths)) else "The objectives are separated and readable.",
            20,
        ),
        Criterion(
            "Objectives use precise action verbs",
            bool(objectives) and all(_contains_any(item, ACTION_PATTERNS) for item in objectives),
            "Start each objective with a precise action such as investigate, examine, compare, evaluate, analyse or determine."
            if not objectives or not all(_contains_any(item, ACTION_PATTERNS) for item in objectives) else "Each objective states an observable research action.",
            25,
        ),
        Criterion(
            "Objectives state what will be found out or achieved",
            len(extract_keywords(combined)) >= 6,
            "Name the exact phenomenon, relationship, outcome or contribution rather than a broad intention."
            if len(extract_keywords(combined)) < 6 else "The objectives identify a specific intended outcome.",
            20,
        ),
        Criterion(
            "Objectives align with research questions",
            len(shared) >= 2,
            "Make every objective traceable to one or more research questions using consistent concepts."
            if len(shared) < 2 else "Shared concepts include: " + ", ".join(shared[:6]) + ".",
            25,
        ),
        Criterion(
            "Value is established elsewhere in the proposal",
            _contains_any(data.introduction + " " + data.expected_results, SIGNIFICANCE_PATTERNS),
            "Ensure the introduction or significance section explains the relevance and value of achieving these objectives."
            if not _contains_any(data.introduction + " " + data.expected_results, SIGNIFICANCE_PATTERNS) else "The proposal explains why achieving the objectives is valuable.",
            10,
        ),
    ]
    return _section("Objectives", criteria)


def _author_year_citations(text: str) -> set[str]:
    surnames = set()
    patterns = (
        r"\(([A-Z][A-Za-z'’-]+)(?:\s+et\s+al\.)?(?:\s*&[^,]+)?,\s*\d{4}[a-z]?\)",
        r"\b([A-Z][A-Za-z'’-]+)(?:\s+et\s+al\.)?\s*\(\d{4}[a-z]?\)",
    )
    for pattern in patterns:
        surnames.update(match.lower() for match in re.findall(pattern, text))
    return surnames


def _numeric_citations(text: str) -> set[int]:
    numbers: set[int] = set()
    for group in re.findall(r"\[([0-9,;\s-]+)\]", text):
        for number in re.findall(r"\d+", group):
            numbers.add(int(number))
    return numbers


def review_literature(data: ProposalInput) -> SectionReview:
    text = _normalise(data.literature_review)
    words = _word_count(text)
    author_citations = _author_year_citations(text)
    numeric_citations = _numeric_citations(text)
    citation_count = len(author_citations) + len(numeric_citations)
    shared = _shared_keywords(text, data.research_questions)
    previous_research = _contains_any(
        text,
        (r"\bprevious (?:research|studies|work)\b", r"\bprior (?:research|studies|work)\b", r"\bexisting literature\b", r"\bstudies (?:have|found|reported|showed|show)\b", r"\bresearch (?:has|have|found|reported|shows)\b"),
    )
    building_new = _contains_any(text, (*GAP_PATTERNS, r"\bbuild(?:s|ing)? on\b", r"\bextend", r"\bnew line of research\b"))
    preliminary = data.preliminary_work_not_applicable or _contains_any(
        text,
        (r"\bpreliminary\b", r"\bpilot\b", r"\bour earlier work\b", r"\bprevious work by the (?:researcher|team|applicant)\b"),
    )
    criteria = [
        Criterion(
            "Provides sufficient synthesis",
            words >= 100,
            f"The literature review contains {words} words. This is a coverage prompt—not an official word limit. Expand the synthesis if key achievements and debates are not yet evident."
            if words < 100 else "The review provides enough material for the synthesis checks.",
            10,
        ),
        Criterion(
            "Uses key references",
            citation_count >= 3,
            "Cite several relevant sources in the text to demonstrate knowledge of the main research in the area."
            if citation_count < 3 else f"The review contains at least {citation_count} distinct citation marker(s).",
            20,
        ),
        Criterion(
            "Synthesises previous research",
            previous_research,
            "Explain what previous studies have established; avoid presenting only an uncited description of the topic."
            if not previous_research else "The review explicitly discusses previous research and its achievements.",
            20,
        ),
        Criterion(
            "Shows how the proposal builds on earlier work",
            building_new,
            "Identify what earlier studies leave unresolved and how the proposed study builds on or extends them."
            if not building_new else "The review establishes a new or extended line of inquiry.",
            20,
        ),
        Criterion(
            "Connects literature to the research questions",
            len(shared) >= 2,
            "Organise the review around the concepts in the research questions and make the relevance explicit."
            if len(shared) < 2 else "Shared concepts include: " + ", ".join(shared[:6]) + ".",
            20,
        ),
        Criterion(
            "Addresses preliminary work where applicable",
            preliminary,
            "Briefly mention relevant preliminary or earlier work by the applicant/team, or select ‘not applicable’."
            if not preliminary else "Preliminary work is addressed or appropriately marked as not applicable.",
            10,
        ),
    ]
    return _section("Brief literature review", criteria)


def review_methodology(data: ProposalInput) -> SectionReview:
    text = _normalise(data.methodology)
    words = _word_count(text)
    framework_ok = data.framework_not_applicable or _contains_any(text, FRAMEWORK_PATTERNS)
    criteria = [
        Criterion(
            "Provides sufficient methodological detail",
            words >= 120,
            f"The methodology contains {words} words. This is a coverage prompt—not an official word limit. Add enough detail for reviewers to judge how the study will be conducted."
            if words < 120 else "The section provides enough material for the methodological checks.",
            10,
        ),
        Criterion(
            "Names and justifies the research approach or design",
            _contains_any(text, DESIGN_PATTERNS),
            "Name the overall research approach or design and explain why it fits the research questions."
            if not _contains_any(text, DESIGN_PATTERNS) else "The proposal identifies a research approach or design.",
            15,
        ),
        Criterion(
            "Specifies data needs and sources",
            _contains_any(text, DATA_SOURCE_PATTERNS),
            "Identify the required data and its source, including participants, sample, documents or dataset where relevant."
            if not _contains_any(text, DATA_SOURCE_PATTERNS) else "The proposal identifies the data and where it will come from.",
            20,
        ),
        Criterion(
            "Explains methods and procedures",
            _contains_any(text, COLLECTION_PATTERNS),
            "Describe how data will be collected and the key procedures or measures used."
            if not _contains_any(text, COLLECTION_PATTERNS) else "Data-collection methods or procedures are described.",
            15,
        ),
        Criterion(
            "Identifies analytic techniques",
            _contains_any(text, ANALYSIS_PATTERNS),
            "Name the qualitative, quantitative or mixed-method analytic techniques that will address the questions."
            if not _contains_any(text, ANALYSIS_PATTERNS) else "The analysis techniques are stated.",
            20,
        ),
        Criterion(
            "Explains how results will be interpreted",
            _contains_any(text, INTERPRETATION_PATTERNS),
            "Explain how analysis will be interpreted, checked or related to the framework, literature or conclusions."
            if not _contains_any(text, INTERPRETATION_PATTERNS) else "The proposal includes a plan for interpreting the results.",
            10,
        ),
        Criterion(
            "States a theoretical or conceptual framework where applicable",
            framework_ok,
            "State the theoretical or conceptual approach, or select ‘not applicable’ if the study does not require one."
            if not framework_ok else "A framework is identified or appropriately marked as not applicable.",
            10,
        ),
    ]
    return _section("Methodology and theoretical framework", criteria)


def review_expected_results(data: ProposalInput) -> SectionReview:
    text = _normalise(data.expected_results)
    cautious = _contains_any(text, (r"\bexpect", r"\banticipat", r"\bmay\b", r"\bmight\b", r"\bhypothes", r"\bpotential"))
    shared = _shared_keywords(text, data.research_questions + " " + data.objectives)
    criteria = [
        Criterion(
            "Describes plausible expected findings",
            _word_count(text) >= 30 and _contains_any(text, (r"\bfindings?\b", r"\bresults?\b", r"\boutcomes?\b", r"\bexpect", r"\banticipat")),
            "Describe the kinds of findings or outcomes the study may produce without presenting them as known facts."
            if _word_count(text) < 30 or not _contains_any(text, (r"\bfindings?\b", r"\bresults?\b", r"\boutcomes?\b", r"\bexpect", r"\banticipat")) else "The proposal describes plausible expected findings.",
            30,
        ),
        Criterion(
            "Uses appropriately cautious language",
            cautious,
            "Use wording such as ‘expected’, ‘anticipated’, ‘may’ or ‘potential’ because the study has not yet been completed."
            if not cautious else "Expected results are framed as provisional rather than predetermined.",
            20,
        ),
        Criterion(
            "Explains significance and contribution",
            _contains_any(text, SIGNIFICANCE_PATTERNS),
            "Explain how the possible findings could contribute to knowledge, policy or practice."
            if not _contains_any(text, SIGNIFICANCE_PATTERNS) else "The possible contribution or value is explained.",
            25,
        ),
        Criterion(
            "Expected results connect to the inquiry",
            len(shared) >= 2,
            "Use the key concepts from the research questions and objectives when discussing expected results."
            if len(shared) < 2 else "Shared concepts include: " + ", ".join(shared[:6]) + ".",
            25,
        ),
    ]
    return _section("Expected results and significance", criteria)


def review_work_plan(data: ProposalInput) -> SectionReview:
    text = _normalise(data.work_plan)
    criteria = [
        Criterion(
            "Describes a workable sequence",
            _word_count(text) >= 40 and _contains_any(text, (r"\bphase", r"\bstage", r"\bstep", r"\bfirst\b", r"\bthen\b", r"\bsubsequent", r"\bsequence")),
            "Outline the main stages in a logical sequence. The length check is a prompt, not an official requirement."
            if _word_count(text) < 40 or not _contains_any(text, (r"\bphase", r"\bstage", r"\bstep", r"\bfirst\b", r"\bthen\b", r"\bsubsequent", r"\bsequence")) else "The work is organised into a clear sequence.",
            25,
        ),
        Criterion(
            "Includes timing or milestones",
            _contains_any(text, (r"\bweek\b", r"\bmonth\b", r"\bsemester\b", r"\byear\b", r"\bmilestone", r"\btimeline", r"\bby \w+ \d{4}\b")),
            "Add indicative timing or milestones so reviewers can judge whether the work can be completed."
            if not _contains_any(text, (r"\bweek\b", r"\bmonth\b", r"\bsemester\b", r"\byear\b", r"\bmilestone", r"\btimeline", r"\bby \w+ \d{4}\b")) else "The plan includes timing or milestones.",
            25,
        ),
        Criterion(
            "Addresses access, people or resources",
            _contains_any(text, (r"\baccess\b", r"\bpermission", r"\brecruit", r"\bteam\b", r"\brole", r"\bresource", r"\bsoftware\b", r"\bbudget\b", r"\bfacilit")),
            "State how access, recruitment, team roles or essential resources will be secured."
            if not _contains_any(text, (r"\baccess\b", r"\bpermission", r"\brecruit", r"\bteam\b", r"\brole", r"\bresource", r"\bsoftware\b", r"\bbudget\b", r"\bfacilit")) else "The plan addresses practical access or resources.",
            25,
        ),
        Criterion(
            "Shows that scope and risks are manageable",
            _contains_any(text, (r"\bscope\b", r"\blimit", r"\brisk", r"\bcontingen", r"\bfeasib", r"\bmanageable\b", r"\bdelay")),
            "Acknowledge a key constraint or risk and show how the project scope remains feasible."
            if not _contains_any(text, (r"\bscope\b", r"\blimit", r"\brisk", r"\bcontingen", r"\bfeasib", r"\bmanageable\b", r"\bdelay")) else "The plan considers feasibility, scope or risks.",
            25,
        ),
    ]
    return _section("Feasibility and work plan", criteria)


def review_references(data: ProposalInput) -> SectionReview:
    entries = [line.strip() for line in data.references.splitlines() if line.strip()]
    body = " ".join(
        [
            data.introduction,
            data.literature_review,
            data.methodology,
            data.expected_results,
        ]
    )
    author_citations = _author_year_citations(body)
    numeric_citations = _numeric_citations(body)
    citation_count = len(author_citations) + len(numeric_citations)
    reference_text = data.references.lower()
    author_matches = sum(1 for surname in author_citations if surname in reference_text)
    author_coverage = author_matches / len(author_citations) if author_citations else 0.0
    numeric_coverage = bool(numeric_citations) and max(numeric_citations) <= len(entries)
    coverage_ok = (author_citations and author_coverage >= 0.8) or numeric_coverage
    year_ratio = (
        sum(bool(re.search(r"\b(?:19|20)\d{2}[a-z]?\b", entry)) for entry in entries) / len(entries)
        if entries else 0.0
    )
    detailed_ratio = sum(_word_count(entry) >= 5 for entry in entries) / len(entries) if entries else 0.0
    criteria = [
        Criterion(
            "Includes a substantive reference list",
            len(entries) >= 3,
            "Place each reference on a separate line and include the key sources cited in the proposal."
            if len(entries) < 3 else f"The list contains {len(entries)} reference entries.",
            20,
        ),
        Criterion(
            "Reference entries contain basic publication details",
            year_ratio >= 0.75 and detailed_ratio >= 0.75,
            "Check that most entries include author, year, title and source details in the required style."
            if year_ratio < 0.75 or detailed_ratio < 0.75 else "Most entries contain a year and sufficient publication detail.",
            20,
        ),
        Criterion(
            "The proposal contains in-text citations",
            citation_count >= 3,
            "Add in-text citations for the research claims and literature discussed. Both author-year and numbered styles are recognised."
            if citation_count < 3 else f"At least {citation_count} distinct citation marker(s) were detected.",
            20,
        ),
        Criterion(
            "Citations appear in the reference list",
            bool(coverage_ok),
            "Cross-check that every in-text citation has a corresponding reference-list entry. Automated matching is approximate, so verify manually."
            if not coverage_ok else "Most detected in-text citations appear to have corresponding reference entries.",
            30,
        ),
        Criterion(
            "One consistent reference style is used",
            bool(entries) and not (author_citations and numeric_citations),
            "Avoid mixing author-year and numbered citation systems unless the required style explicitly permits it."
            if author_citations and numeric_citations else "The detected citations use one broad referencing system; confirm detailed style manually.",
            10,
        ),
    ]
    return _section("References", criteria)


def review_alignment(data: ProposalInput) -> SectionReview:
    rq_objectives = _shared_keywords(data.research_questions, data.objectives)
    rq_literature = _shared_keywords(data.research_questions, data.literature_review)
    inquiry = data.research_questions + " " + data.objectives
    method_alignment = _shared_keywords(inquiry, data.methodology)
    title_alignment = _shared_keywords(data.title, data.introduction + " " + inquiry)
    why_present = _contains_any(data.introduction + " " + data.literature_review + " " + data.expected_results, (*GAP_PATTERNS, *SIGNIFICANCE_PATTERNS))
    what_present = bool(data.research_questions.strip() and data.objectives.strip())
    how_present = _contains_any(data.methodology, (*DESIGN_PATTERNS, *COLLECTION_PATTERNS, *ANALYSIS_PATTERNS))
    criteria = [
        Criterion(
            "Title reflects the proposed inquiry",
            len(title_alignment) >= 1,
            "Use key concepts from the title consistently in the introduction, questions or objectives."
            if len(title_alignment) < 1 else "The title and proposal share a clear focus.",
            15,
        ),
        Criterion(
            "Research questions and objectives align",
            len(rq_objectives) >= 2,
            "Map each objective to a research question and use consistent terminology."
            if len(rq_objectives) < 2 else "Shared concepts include: " + ", ".join(rq_objectives[:6]) + ".",
            25,
        ),
        Criterion(
            "Literature review supports the questions",
            len(rq_literature) >= 2,
            "Ensure the literature review establishes the concepts and gap addressed by the research questions."
            if len(rq_literature) < 2 else "The literature and questions share a clear conceptual focus.",
            20,
        ),
        Criterion(
            "Methodology can address the inquiry",
            len(method_alignment) >= 1,
            "Explain how the selected data and analysis will answer each research question or objective."
            if len(method_alignment) < 1 else "The methodology uses concepts connected to the inquiry.",
            20,
        ),
        Criterion(
            "The proposal answers what, why and how",
            what_present and why_present and how_present,
            "Check that a reviewer can quickly identify what will be studied, why it is worthwhile and how it will be done."
            if not (what_present and why_present and how_present) else "The proposal contains identifiable evidence for what, why and how.",
            20,
        ),
    ]
    return _section("Overall alignment", criteria)


def review_proposal(data: ProposalInput) -> ProposalReview:
    sections = (
        review_introduction(data),
        review_research_questions(data),
        review_objectives(data),
        review_literature(data),
        review_methodology(data),
        review_expected_results(data),
        review_work_plan(data),
        review_references(data),
        review_alignment(data),
    )
    overall = round(
        sum(section.score * SECTION_WEIGHTS[section.name] for section in sections) / 100
    )
    return ProposalReview(overall_score=overall, label=_label(overall), sections=sections)


def priority_actions(review: ProposalReview, limit: int = 8) -> list[tuple[str, str, int]]:
    failed = [
        (section.name, criterion.feedback, criterion.weight * SECTION_WEIGHTS[section.name])
        for section in review.sections
        for criterion in section.criteria
        if not criterion.passed
    ]
    failed.sort(key=lambda item: item[2], reverse=True)
    return [(section, feedback, impact) for section, feedback, impact in failed[:limit]]


def build_report(data: ProposalInput, review: ProposalReview) -> str:
    lines = [
        "RESEARCH PROPOSAL SELF-REVIEW",
        "=" * 38,
        "",
        f"Proposal title: {data.title.strip() or '[Not entered]'}",
        f"Overall readiness indicator: {review.overall_score}/100 — {review.label}",
        "",
        "PRIORITY REVISION ACTIONS",
        "-" * 25,
    ]
    priorities = priority_actions(review)
    if priorities:
        for number, (section, feedback, _impact) in enumerate(priorities, start=1):
            lines.append(f"{number}. [{section}] {feedback}")
    else:
        lines.append("All automated checks are met. Complete the final human checks below.")

    for section in review.sections:
        lines.extend(["", section.name.upper(), f"Score: {section.score}/100 — {section.label}"])
        for item in section.criteria:
            status = "MEETS CHECK" if item.passed else "REVIEW"
            lines.append(f"[{status}] {item.title}: {item.feedback}")

    lines.extend(
        [
            "",
            "FINAL HUMAN CHECKS",
            "-" * 18,
            "- Can an evaluator identify what will be studied, why it matters and how it will be done?",
            "- Is every claim about previous research supported by an appropriate citation?",
            "- Does each research question map to an objective, data source and analytic technique?",
            "- Are proposed results presented as expectations rather than predetermined conclusions?",
            "- Is every in-text citation included in the reference list and vice versa?",
            "- Have the required institutional format, word limits and submission instructions been checked?",
            "",
            "This is a formative readiness indicator based on transparent language checks. It is not an official evaluation score and cannot judge the accuracy, originality or disciplinary quality of the proposal.",
        ]
    )
    return "\n".join(lines)
