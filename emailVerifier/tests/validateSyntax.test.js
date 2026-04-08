const test = require('node:test');
const assert = require('node:assert/strict');

const { normalizeEmail, validateSyntax, maskEmail } = require('../lib/validateSyntax');

test('normalizeEmail trims and lowercases', () => {
  assert.equal(normalizeEmail('  Alice+TAG@Example.COM  '), 'alice+tag@example.com');
});

test('validateSyntax accepts RFC-like valid email', () => {
  const result = validateSyntax('alice.smith+tag@example.com');
  assert.equal(result.syntaxValid, true);
  assert.equal(result.email, 'alice.smith+tag@example.com');
  assert.equal(result.syntaxError, null);
});

test('validateSyntax rejects invalid email', () => {
  const result = validateSyntax('not-an-email');
  assert.equal(result.syntaxValid, false);
  assert.equal(result.syntaxError, 'Invalid email syntax');
});

test('maskEmail masks local part and preserves domain', () => {
  assert.equal(maskEmail('alice@example.com'), 'a***@example.com');
  assert.equal(maskEmail('x@example.com'), '*@example.com');
  assert.equal(maskEmail('bad-email'), '***invalid***');
});
