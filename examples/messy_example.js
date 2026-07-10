function loadUser(raw) {
  const parsed = JSON.parse(raw)
  const result = eval(parsed.expression)
  return result
}

// TODO: add tests for invalid input
const repeated = "this string is repeated in a suspicious way";
const repeatedAgain = "this string is repeated in a suspicious way";
const repeatedThird = "this string is repeated in a suspicious way";
