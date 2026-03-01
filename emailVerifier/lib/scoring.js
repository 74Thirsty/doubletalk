function classifyStatus({ syntaxValid, domainExists, mxFound, smtpResult, disposable, roleBased }) {
  if (!syntaxValid) {
    return { status: "invalid", notes: "Invalid syntax" };
  }

  if (!domainExists || !mxFound) {
    return { status: "invalid", notes: "Domain or MX missing" };
  }

  if (smtpResult === "rejected") {
    return { status: "invalid", notes: "Mailbox explicitly rejected" };
  }

  if (smtpResult === "accepted" && !disposable && !roleBased) {
    return { status: "valid", notes: "SMTP accepted" };
  }

  if (smtpResult === "temporary_failure" || smtpResult === "unknown") {
    return { status: "unknown", notes: "SMTP inconclusive" };
  }

  if (disposable || roleBased || smtpResult === "not_attempted") {
    return { status: "risky", notes: "Disposable, role-based, or SMTP not attempted" };
  }

  return { status: "unknown", notes: "Unable to determine" };
}

module.exports = { classifyStatus };
