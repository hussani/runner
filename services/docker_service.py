from typing import List, Tuple
import env

from docker import DockerClient, types
from utils.docker_container import DockerContainer
from models.docker_image_name import DockerImageName
from builders.docker_container_builder import DockerContainerBuilder
from services.docker_image_name_service import DockerImageNameService

KB = 1024
MB = 1024 * KB

class DockerService():
  def __init__(
    self,
    dockerClient: DockerClient,
    dockerImageNameService: DockerImageNameService,
    dockerContainerBuilder: DockerContainerBuilder,
  ) -> None:
    self.dockerClient = dockerClient
    self.dockerImageNameService = dockerImageNameService
    self.dockerContainerBuilder = dockerContainerBuilder

  def pullImage(self, imageName: DockerImageName) -> None:
    processedImageName = self.dockerImageNameService.getProcessedImageName(imageName)
    self.dockerClient.images.pull(processedImageName)

  def runAndGetContainer(self, imageName: DockerImageName, testCommand: str, identifier: str) -> DockerContainer:
    processedImageName = self.dockerImageNameService.getProcessedImageName(imageName)
    container = self.dockerClient.containers.run(
      processedImageName,
      testCommand,
      detach=True,
      auto_remove=True,
      working_dir=env.DOCKER_WORKDIR,
      volumes=[f"{env.PROJECT_TMP_DIRECTORY}/{identifier}:{env.DOCKER_TMP_DIRECTORY}"],
      network_mode="none",
      pids_limit=128,
      kernel_memory="768m",
      mem_limit="768m",
      ulimits=self.getUlimits([
        ('core', 0),
        ('fsize', 128*MB),
        ('locks', 1024),
        ('nofile', 1024),
        ('nproc', 1024),
        ('stack', 16*MB),
      ])
    )
    return self.dockerContainerBuilder.buildContainer(container)

  def getUlimits(self, ulimitDefinitions: List[Tuple[str, int]]) -> List[types.Ulimit]:
    ulimits: List[types.Ulimit] = [];

    for name, value in ulimitDefinitions:
      ulimits.append(types.Ulimit(name=name, soft=value, hard=value))
    
    return ulimits
