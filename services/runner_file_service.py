import shutil
import uuid
from pathlib import Path
from typing import List

import env
from models.run_request import RunRequestFile


class RunnerFileService():
  def createFile(self, filename: str, content: str, identifier: uuid) -> None:
    file = Path(f"{env.PROJECT_TMP_DIRECTORY}/{identifier}/{filename}")
    file.parent.mkdir(exist_ok=True, parents=True)
    file.write_text(content)

  def createFiles(self, files: List[RunRequestFile], identifier: uuid) -> None:
    for file in files:
      self.createFile(file.fileName, file.content, identifier)

  @staticmethod
  def deleteDirectory(identifier: uuid) -> None:
    directory = Path(f"{env.PROJECT_TMP_DIRECTORY}/{identifier}")
    shutil.rmtree(directory)
