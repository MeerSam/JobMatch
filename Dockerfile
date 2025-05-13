FROM python:3.12.10-slim

WORKDIR /

# RUN apt-get update && apt-get install -y \
#     build-essential \
#     curl \
#     software-properties-common \
#     git \
#     && rm -rf /var/lib/apt/lists/*


# Copy all project files
COPY . .

 
# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
 
RUN python -m spacy download en_core_web_lg



# Expose ports for FastAPI and Streamlit
EXPOSE 8000
EXPOSE 8501



# Create a startup script
RUN echo '#!/bin/bash\n\
# Start FastAPI in background\n\
uvicorn main:app --host 0.0.0.0 --port 8000 &\n\
# Start Streamlit\n\
streamlit run src/streamlit_app.py --server.port 8501 --server.address 0.0.0.0\n\
' > /start.sh && chmod +x /start.sh

# Set the entry point
ENTRYPOINT ["/start.sh"]