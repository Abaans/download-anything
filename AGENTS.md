# Repository guidance

These are portable agent instructions, not application automation services. Keep each skill self-contained under skills/<name> with matching frontmatter and accurate capability requirements.

Preserve the user's requested stage and existing authorization. Do not add automatic installation, account access, messages, publishing or payments to a workflow. Use fictional examples and exclude private documents, account details, machine-specific paths and generated runtime artifacts.

Run `python3 -m unittest discover -s tests -v` and `python3 tools/validate.py` after changes. Install development requirements in an isolated environment. Live Word, Jira, Figma and authenticated-source operations require their own scoped testing; static tests cannot certify them.

Do not publish, commit or create a release without the owner's request. Keep platform and compatibility claims tied to observed evidence.
