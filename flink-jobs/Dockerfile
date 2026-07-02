FROM python:3.11-slim

WORKDIR /opt/flink-jobs

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy job files
COPY flink_job.py .
COPY wait_for_services.py .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh wait_for_services.py

ENTRYPOINT ["/opt/flink-jobs/entrypoint.sh"]
