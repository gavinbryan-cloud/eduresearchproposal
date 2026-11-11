# Research Proposal Self-Review

A transparent, rule-based Streamlit app for formative review of a research proposal before submission for evaluation. The content and checks are based on the supplied SP research proposal guidance.

The app does not use a generative AI service, require an API key, store proposals in a database, award marks, or predict an evaluator's decision.

## What the app reviews

- Introduction and significance
- Fully stated research questions or hypotheses
- Clear and aligned objectives
- Brief literature review and key references
- Methodology and theoretical or conceptual framework
- Expected results and contribution
- Feasibility and work plan
- In-text citations and reference list
- Alignment across the title, questions, objectives, literature and methodology

Students receive section scores, criterion-level feedback, prioritised revision actions, final human checks and a downloadable text report.

## Important interpretation

The scores are readiness indicators based on transparent coverage and language checks. They are not an official rubric. Approximate length checks are prompts to detect sections that may be too brief; they are not official word limits.

The app cannot determine whether a claimed research gap is true, whether a method is suitable, whether the study is original, or whether references are accurate. These require source checking and disciplinary judgement.

## Run locally

1. Install Python 3.10 or later.
2. Open a terminal in this folder.
3. Install the dependency:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the app:

   ```bash
   streamlit run app.py
   ```

## Upload to GitHub

Create a GitHub repository and place the contents of this folder at its root:

```text
.
├── .streamlit/
│   └── config.toml
├── tests/
│   └── test_review_engine.py
├── app.py
├── review_engine.py
├── requirements.txt
└── README.md
```

Commit the files to the `main` branch.

## Deploy on Streamlit Community Cloud

1. Sign in to Streamlit Community Cloud with GitHub.
2. Create an app and select the repository and `main` branch.
3. Set the entrypoint to `app.py`.
4. Deploy. No secrets or environment variables are required.

## Customise the app

- Edit visible guidance and scaffolds in `app.py`.
- Edit patterns, weights and feedback in `review_engine.py`.
- Keep each section's criterion weights at 100.
- Keep `SECTION_WEIGHTS` at a total of 100.
- Adjust colours in `.streamlit/config.toml` and the CSS block in `app.py`.

## Testing

Run the included tests from the repository root:

```bash
python -m unittest discover -s tests -v
```
