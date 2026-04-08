const test = require('node:test');
const assert = require('node:assert/strict');

const { classifyStatus } = require('../lib/scoring');

test('classifyStatus returns invalid for bad syntax', () => {
  const result = classifyStatus({
    syntaxValid: false,
    domainExists: true,
    mxFound: true,
    smtpResult: 'accepted',
    disposable: false,
    roleBased: false,
  });

  assert.deepEqual(result, { status: 'invalid', notes: 'Invalid syntax' });
});

test('classifyStatus returns valid for accepted non-disposable non-role account', () => {
  const result = classifyStatus({
    syntaxValid: true,
    domainExists: true,
    mxFound: true,
    smtpResult: 'accepted',
    disposable: false,
    roleBased: false,
  });

  assert.deepEqual(result, { status: 'valid', notes: 'SMTP accepted' });
});

test('classifyStatus returns risky when SMTP not attempted', () => {
  const result = classifyStatus({
    syntaxValid: true,
    domainExists: true,
    mxFound: true,
    smtpResult: 'not_attempted',
    disposable: false,
    roleBased: false,
  });

  assert.deepEqual(result, {
    status: 'risky',
    notes: 'Disposable, role-based, or SMTP not attempted',
  });
});

test('classifyStatus returns unknown on temporary SMTP failure', () => {
  const result = classifyStatus({
    syntaxValid: true,
    domainExists: true,
    mxFound: true,
    smtpResult: 'temporary_failure',
    disposable: false,
    roleBased: false,
  });

  assert.deepEqual(result, { status: 'unknown', notes: 'SMTP inconclusive' });
});
