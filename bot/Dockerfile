# Bot Dockerfile
# Uses uv for dependency management (not pip/requirements.txt)

FROM python:3.12-slim

# Install uv
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy pyproject.toml, uv.lock (if exists), and README.md for build
COPY pyproject.toml uv.lock* README.md* ./

# Install dependencies using uv
# --frozen ensures reproducible builds from lock file
RUN uv sync --frozen 2>/dev/null || uv sync

# Copy bot source code
COPY bot.py config.py ./
COPY handlers/ ./handlers/
COPY services/ ./services/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run the bot
CMD ["uv", "run", "python", "bot.py"]
