# AI notes

OpenAI Codex assisted with reading the supplied brief, setting up the FastAPI scaffold, drafting the agreed specification and implementing the backend and tests. The user selected the architecture and resolved product ambiguities; the submitter remains responsible for reviewing and explaining the code.

Examples of prompts used:

- Ask Codex to read the backend and business rules in the take-home PDF and set up the project workflow.
- Ask Codex to implement the agreed backend specification, exercise real PostgreSQL integration tests, review security and preserve existing work.

One incorrect AI statement during architecture planning said the brief did not prescribe a folder layout. The user questioned it; rereading page 4 showed that the submission must contain `backend/` and `frontend/` directories. The architecture proposal was corrected to distinguish that requirement from the unspecified internal backend folder names. This repository currently contains the backend alone, so a complete submission still needs the required combined layout.

During this implementation, separate reviews identified invalid Unicode and duplicate JSON inputs, slow request bodies holding database connections, missing HTTP error headers, and a risk of database-pool stalls when concurrent requests yield while holding connections. A follow-up review also found that an extreme JSON exponent could trigger an uncaught decimal parsing error. The implementation was adjusted and regression cases were added, including a concurrent request burst and the extreme exponent. Each commit is reviewed through its staged diff and applicable checks; the final PR is reviewed again against the spec and security boundaries. Automated checks do not replace human review.

No real credentials or secrets were added. `.env.example` contains local placeholder values only. Approximate time across prior sessions was not recorded and must be supplied by the submitter before submission.
