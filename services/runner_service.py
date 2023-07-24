import uuid

from builders.test_verifier_builder import TestVerifierBuilder
from models.docker_image_name import DockerImageName
from models.run_request import RunRequestBody, RunRequestResponse
from services.docker_image_map_service import DockerImageMapService
from services.docker_service import DockerService
from services.runner_file_service import RunnerFileService


class RunnerService():
  def __init__(
    self,
    dockerService: DockerService,
    runnerFileService: RunnerFileService,
    dockerImageMapService: DockerImageMapService,
    testVerifierBuilder: TestVerifierBuilder,
  ) -> None:
    self.dockerService = dockerService
    self.runnerFileService = runnerFileService
    self.dockerImageMapService = dockerImageMapService
    self.testVerifierBuilder = testVerifierBuilder

  def run(self, body: RunRequestBody) -> RunRequestResponse:

    uniqueIdentifier = uuid.uuid4()

    files = body.files
    testCommand = body.testCommand
    dockerImageName = self.dockerImageMapService.getDockerImageFromTestingEnvironment(body.testingEnvironment)
    testVerifier = self.testVerifierBuilder.build(body.testingEnvironment)

    self.runnerFileService.createFiles(files, uniqueIdentifier)

    dockerContainerOutput = self.runTestAndGetOutput(dockerImageName, testCommand, uniqueIdentifier)

    testPassed = None

    if testVerifier is not None:
      testPassed = testVerifier.testPassed(dockerContainerOutput);

    self.runnerFileService.deleteDirectory(uniqueIdentifier)

    return { 'passed': testPassed, 'output': dockerContainerOutput }

  def runTestAndGetOutput(self, dockerImageName: DockerImageName, testCommand: str, identifier: uuid) -> str:
    dockerContainer = self.dockerService.runAndGetContainer(dockerImageName, testCommand, identifier)
    dockerContainerLogStream = dockerContainer.logs()
    
    dockerContainerOutput = ""

    try:
      while True:
        dockerContainerOutput += next(dockerContainerLogStream).decode("utf-8")
    except StopIteration:
      pass

    return dockerContainerOutput