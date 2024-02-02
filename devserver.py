from pathlib import Path

import uvicorn
from dotenv import load_dotenv

# Loading .env variables
dotenv_path = Path(".env")
load_dotenv(dotenv_path=dotenv_path)

if __name__ == "__main__":
    uvicorn.run("project.main:app", host="0.0.0.0", log_level="info", reload=True, port=8000)
