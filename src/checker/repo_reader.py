import requests
import base64

from pathlib import Path
from src.utils._logger import logger


class GitHubRepoReader:
    """
    Read files of a repository from GitHub REST API
    """

    API_BASE_URL = "https://api.github.com/repos"

    def __init__(self, repo_name: str, branch_name: str = "main"):
        """
        Initialize the reader with the repository name.

        Args:
            repo_name (str): The name of the GitHub repository (e.g., 'psf/requests').
        Raises:
            ValueError: If the provided repository name is invalid.
        """
        self.repo_name = repo_name
        self.branch_name = branch_name
        self.repo_api_url = f"{self.API_BASE_URL}/{self.repo_name}"

    def get_file_content(self, file_path: str) -> str | None:
        """
        Get the content of a file from the GitHub repository.
        """
        file_api_url = f"{self.repo_api_url}/contents/{file_path}?ref={self.branch_name}"

        try:
            response = requests.get(file_api_url)
            response.raise_for_status()

            data = response.json()
            if "content" in data and "encoding" in data and data["encoding"] == "base64":
                encoded_content = data["content"]
                decoded_bytes = base64.b64decode(encoded_content)
                decoded_content = decoded_bytes.decode("utf-8")
                return decoded_content
            else:
                logger.error("Error: API response is missing 'content' or 'encoding' fields.")
                return None

        except requests.exceptions.HTTPError as http_err:
            if http_err.response.status_code == 404:
                logger.error(f"Error: File '{file_path}' not found in repository '{self.repo_name}'.")
            else:
                logger.error(f"HTTP error raises: {http_err}")
            return None
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Request error raises: {req_err}")
            return None
        except Exception as e:
            logger.error(f"Unknown error raises: {e}")
            return None


class LocalRepoReader:
    """
    Read files of a local repository
    """

    def __init__(self, repo_path: str):
        """
        Initialize the reader with the local repository path.

        Args:
            repo_path (str): The path to the local repository.
        """
        self.repo_path = Path(repo_path)
        if not self.repo_path.is_dir():
            raise ValueError(f"Local repository path: {repo_path} not exsists!")

    def get_file_content(self, file_path: str) -> str | None:
        """
        Get the content of a file from the local repository.
        """
        full_path = self.repo_path / file_path

        if not full_path.is_file():
            logger.error(f"Error: File '{file_path}' not found in local repository.")
            return None
        return full_path.read_text(encoding="utf-8")


if __name__ == "__main__":
    ql_reader = GitHubRepoReader(repo_name="github/codeql", branch_name="codeql-cli-2.23.0")
    print(ql_reader.get_file_content("java/ql/src/Security/CWE/CWE-022/ZipSlip.ql"))
