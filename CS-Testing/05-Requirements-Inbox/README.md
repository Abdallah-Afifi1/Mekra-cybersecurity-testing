# Requirements inbox

Put the requirements for each feature here, one file per feature (Word, Excel, PDF, Markdown or CSV all work), named `<feature>_<source-doc>_<version>`, for example `UCM_SoftwareDownload_SRS_rev731696.xlsx`.

For each feature, please include or tell me:

1. The requirement IDs and text, and the document version they come from.
2. The priority or the ASIL/CAL level, if one is assigned.
3. Anything already decided for the open `[X]` choices (for example the RSA key length, or the debug challenge validity period).
4. Whether the feature is tested at system level, software level, or both.

What I do with each feature:

1. Add its requirements to `../03-Traceability/`.
2. Write the test cases (preconditions, steps, expected result, pass/fail criterion, needed equipment) in `../01-System/` or `../02-Software/`.
3. Flag blockers in `../04-Test-Environment/cs_bench_gap_analysis.md`.
4. Once the bench items are settled, write the test scripts in the existing iTestStudio format.
