from dotenv import load_dotenv
import os

# JDK-Path for dsl-kirin: jdk17
KIRIN_JAVA_HOME = "xxxx"

# dsl_kirin cli path
KIRIN_CLI_PATH = "xxxx"

# llm config
OPENAI_BASE_URL = "xxxxx"
OPENAI_MODEL_NAME = "xxxxx"

# api keys in env
load_dotenv("src/.env", override=True)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
