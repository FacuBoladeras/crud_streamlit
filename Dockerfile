# Use the official Python image as base
FROM python:3.12.0

# Set working directory to /app
WORKDIR /app

# Copy requirements.txt
COPY requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies
RUN pip install -r requirements.txt

# Copy all app files
COPY . .

# Expose Streamlit port
EXPOSE 8501


# Run Streamlit app on container start
CMD ["streamlit", "run" ,"app.py"]
