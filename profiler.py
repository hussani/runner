from dependency_container import runnerService
from models.run_request import RunRequestBody


def run():
    body = RunRequestBody(
        testCommand="jest",
        files=[
            {"fileName": "sum.js",
             "content": "\"use strict\";\n\nfunction sum(a, b) {\n  return a + b;\n}\n\nmodule.exports = { sum };\n"},
            {"fileName": "sum.test.js",
             "content": "\"use strict\";\n\nconst { sum } = require(\"./sum.js\");\n\ntest(\"should return proper "
                        "result\", () => {\n  expect(sum(1, 1)).toBe(2);\n  expect(sum(-1, 1)).toBe(0);\n  expect("
                        "sum(-1, -1)).toBe(-2);\n});"}
        ],
        testingEnvironment="javascript-jest"
    )
    runnerService.run(body)


if __name__ == "__main__":
    run()
