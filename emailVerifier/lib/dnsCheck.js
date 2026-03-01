const dns = require("node:dns/promises");

async function dnsCheck(domain) {
  if (!domain) {
    return {
      domain,
      mxFound: false,
      mxRecords: [],
      hasA: false,
      hasAAAA: false,
      domainExists: false,
      notes: "Missing domain",
    };
  }

  const result = {
    domain,
    mxFound: false,
    mxRecords: [],
    hasA: false,
    hasAAAA: false,
    domainExists: false,
    notes: "",
  };

  try {
    const mx = await dns.resolveMx(domain);
    if (mx && mx.length > 0) {
      result.mxFound = true;
      result.mxRecords = mx.sort((a, b) => a.priority - b.priority);
    }
  } catch {
    result.notes = "MX lookup failed";
  }

  try {
    const aRecords = await dns.resolve4(domain);
    result.hasA = aRecords.length > 0;
  } catch {
    // ignore
  }

  try {
    const aaaaRecords = await dns.resolve6(domain);
    result.hasAAAA = aaaaRecords.length > 0;
  } catch {
    // ignore
  }

  result.domainExists = result.mxFound || result.hasA || result.hasAAAA;

  if (!result.domainExists) {
    result.notes = result.notes ? `${result.notes}; no A/AAAA records` : "No MX or A/AAAA records";
  }

  return result;
}

module.exports = { dnsCheck };
