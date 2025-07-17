FROM nikolaik/python-nodejs:python3.12-nodejs22-slim

# Python Optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Working Directory
WORKDIR /app

# Copy only requirements first to leverrage Docker cache
COPY ./requirements.txt ./

# Install Dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000