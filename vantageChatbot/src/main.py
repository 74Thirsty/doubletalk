import uvicorn

from src.app import app
from src.utils.logging import configure_logging


if __name__ == '__main__':
    configure_logging()
    uvicorn.run(app, host='0.0.0.0', port=8000)
