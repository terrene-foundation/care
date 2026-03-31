# Security Rules

## Scope

These rules apply to ALL changes in the repository.

## MUST Rules

### 1. No Sensitive Information in Documents

Documents MUST NOT contain:

- Real API keys, passwords, or tokens
- Personal contact information (phone numbers, personal emails) unless explicitly authorized
- Internal IP addresses or infrastructure details
- Draft legal opinions marked as privileged

**Acceptable**: Public email addresses (e.g., info@terrene.foundation), public URLs, published contact details.

### 2. No .env in Git

MUST NOT commit .env files to version control.

**Required**:

- .env in .gitignore
- .env.example for templates (no real values)

### 3. No Hardcoded Secrets in Scripts

Hook scripts and CI scripts MUST NOT contain hardcoded credentials.

**Correct Pattern**:

```
api_key = process.env.API_KEY
```

## MUST NOT Rules

### 1. No Confidential Partnership Details in Public Docs

MUST NOT include confidential terms, pricing, or negotiation details in documents that may become public. Use `[CONFIDENTIAL]` markers and separate confidential annexes.

### 2. No Unredacted PII

MUST NOT include personal data (NRIC, passport numbers, personal addresses) in governance documents without explicit consent and legitimate purpose.

## Governance-Specific Security

### Constitutional Documents

- Review for unintended information disclosure before committing
- Ensure draft clauses don't expose negotiation positions
- Verify cross-references are accurate (broken clause references create ambiguity)

### Partnership Documents

- Government engagement plans may contain sensitive positioning — review before committing
- Grant applications may contain financial projections — ensure appropriate access controls

## Exceptions

Security exceptions require:

1. Written justification
2. Approval from security-reviewer
3. Documentation in the commit message
