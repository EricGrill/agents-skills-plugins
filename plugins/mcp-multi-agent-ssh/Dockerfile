# MCP Multi-Agent SSH Docker Image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY src/ src/

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Create directory for credentials (will be mounted)
RUN mkdir -p /root/.mcp-multi-agent-ssh && chmod 700 /root/.mcp-multi-agent-ssh

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the MCP server
CMD ["python", "-m", "mcp_multi_agent_ssh.server"]
