from fastapi import FastAPI
from models import RunRequest
from utils.file import createFiles, deleteDirectory
import docker
import os

DOCKER_JAVASCRIPT_JEST_IMAGE_NAME = 'vinigpereira/javascript-jest:latest'
DOCKER_JAVASCRIPT_JEST_TEST_COMMAND = 'jest tmp'
DOCKER_CONTAINER_WORKDIR = '/sandbox'
TMP_DIRECTORY_NAME = 'tmp'
TMP_SANDBOX_DIRECTORY_PATH = f"{DOCKER_CONTAINER_WORKDIR}/tmp"

app = FastAPI()

@app.get("/")
async def root():
  return {"message": "Welcome to Testity!"}

@app.post("/run")
async def run(runRequest: RunRequest):
  currentPath = os.path.dirname(os.path.abspath(__file__))
  tmpDirectoryPath = f"{currentPath}/{TMP_DIRECTORY_NAME}"

  createFiles(tmpDirectoryPath, runRequest.files);

  logStream = None

  try:
    client = docker.from_env()
    client.images.pull(DOCKER_JAVASCRIPT_JEST_IMAGE_NAME)
    container = client.containers.run(
      DOCKER_JAVASCRIPT_JEST_IMAGE_NAME,
      DOCKER_JAVASCRIPT_JEST_TEST_COMMAND,
      detach=True,
      working_dir=DOCKER_CONTAINER_WORKDIR,
      volumes=[f"{tmpDirectoryPath}:{TMP_SANDBOX_DIRECTORY_PATH}"]
    )
    logStream = container.logs(stream=True);
  finally:
    deleteDirectory(tmpDirectoryPath, runRequest.files)
  
  finalLog = ""

  try:
    while True:
      finalLog += next(logStream).decode("utf-8")
  except StopIteration:
    print("log iteration stopped")

  return finalLog