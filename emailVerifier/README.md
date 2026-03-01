# Email Verifier (List Hygiene)

A safe, non-invasive email list hygiene CLI that performs:

- syntax validation
- domain existence checks
- MX checks
- optional SMTP RCPT best-effort checks (no message body sent)
- disposable-domain and role-account flags
- status scoring (`valid`, `risky`, `invalid`, `unknown`)

## Setup

```bash
cd emailVerifier
npm install
cp .env.example .env
```

## Run

```bash
node index.js --in inputEmails.csv --out results.csv
```

Optional flags:

```bash
node index.js --in inputEmails.csv --out results.csv --concurrency 3 --smtp true
```

## Input CSV format

Required column:

- `email`

Example:

```csv
email
user@example.com
info@example.com
```

## Output CSV columns

- `emailMasked`
- `syntaxValid`
- `domain`
- `mxFound`
- `smtpResultCode`
- `disposable`
- `roleBased`
- `status`
- `notes`

## Notes

- Full emails are masked in console logs.
- SMTP checks are best-effort and can be blocked by remote providers.
- The tool does not perform website signups, brute force attempts, or send message bodies.
