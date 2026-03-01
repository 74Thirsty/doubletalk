const net = require("node:net");

function parseCode(line) {
  const match = String(line).match(/^(\d{3})/);
  return match ? Number(match[1]) : null;
}

function readResponse(socket, timeoutMs) {
  return new Promise((resolve, reject) => {
    let buffer = "";
    const timer = setTimeout(() => {
      cleanup();
      reject(new Error("SMTP timeout waiting for response"));
    }, timeoutMs);

    const onData = (chunk) => {
      buffer += chunk.toString("utf8");
      const lines = buffer.split(/\r?\n/).filter(Boolean);
      const lastLine = lines[lines.length - 1] || "";
      if (/^\d{3}\s/.test(lastLine)) {
        cleanup();
        resolve({
          code: parseCode(lastLine),
          message: lines.join(" | "),
        });
      }
    };

    const onError = (err) => {
      cleanup();
      reject(err);
    };

    function cleanup() {
      clearTimeout(timer);
      socket.off("data", onData);
      socket.off("error", onError);
    }

    socket.on("data", onData);
    socket.on("error", onError);
  });
}

async function sendCommand(socket, command, timeoutMs) {
  socket.write(`${command}\r\n`);
  return readResponse(socket, timeoutMs);
}

async function smtpCheck({ email, mxRecords, timeoutMs, mailFrom, hostname }) {
  const response = {
    attempted: false,
    smtpResultCode: "",
    smtpResult: "not_attempted",
    notes: "",
  };

  if (!mxRecords || mxRecords.length === 0) {
    response.notes = "No MX records; SMTP skipped";
    return response;
  }

  const targetHost = mxRecords[0].exchange;
  response.attempted = true;

  const socket = net.connect({ host: targetHost, port: 25, timeout: timeoutMs });

  try {
    await new Promise((resolve, reject) => {
      socket.once("connect", resolve);
      socket.once("error", reject);
      socket.once("timeout", () => reject(new Error("SMTP connection timed out")));
    });

    let r = await readResponse(socket, timeoutMs);
    if (!r.code || r.code >= 400) {
      throw new Error(`SMTP greeting failed: ${r.message}`);
    }

    r = await sendCommand(socket, `EHLO ${hostname}`, timeoutMs);
    if (r.code && r.code >= 400) {
      r = await sendCommand(socket, `HELO ${hostname}`, timeoutMs);
      if (!r.code || r.code >= 400) {
        throw new Error(`EHLO/HELO failed: ${r.message}`);
      }
    }

    r = await sendCommand(socket, `MAIL FROM:<${mailFrom}>`, timeoutMs);
    if (!r.code || r.code >= 400) {
      throw new Error(`MAIL FROM rejected: ${r.message}`);
    }

    r = await sendCommand(socket, `RCPT TO:<${email}>`, timeoutMs);
    response.smtpResultCode = r.code ? String(r.code) : "";

    if (r.code === 250 || r.code === 251) {
      response.smtpResult = "accepted";
      response.notes = "RCPT accepted";
    } else if (r.code === 550 || r.code === 551 || r.code === 553) {
      response.smtpResult = "rejected";
      response.notes = r.message;
    } else if (r.code === 450 || r.code === 451 || r.code === 452 || r.code === 421) {
      response.smtpResult = "temporary_failure";
      response.notes = r.message;
    } else {
      response.smtpResult = "unknown";
      response.notes = r.message;
    }

    await sendCommand(socket, "QUIT", timeoutMs);
  } catch (err) {
    response.smtpResult = response.smtpResult === "not_attempted" ? "unknown" : response.smtpResult;
    response.notes = response.notes || err.message || "SMTP check failed";
  } finally {
    socket.destroy();
  }

  return response;
}

module.exports = { smtpCheck };
