const EMAIL_REGEX = /^[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+$/i;

function normalizeEmail(email) {
  return String(email || "").trim().toLowerCase();
}

function maskEmail(email) {
  const normalized = normalizeEmail(email);
  const [localPart, domain] = normalized.split("@");

  if (!localPart || !domain) {
    return "***invalid***";
  }

  if (localPart.length <= 1) {
    return `*@${domain}`;
  }

  return `${localPart[0]}***@${domain}`;
}

function validateSyntax(email) {
  const normalized = normalizeEmail(email);
  const syntaxValid = EMAIL_REGEX.test(normalized);

  return {
    email: normalized,
    syntaxValid,
    syntaxError: syntaxValid ? null : "Invalid email syntax",
  };
}

module.exports = {
  normalizeEmail,
  validateSyntax,
  maskEmail,
};
