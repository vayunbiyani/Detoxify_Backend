FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY /etc/ssl/certs/your_certificate.crt /etc/ssl/certs/
COPY /etc/ssl/private/your_private.key /etc/ssl/private/
COPY requirements.txt .
COPY cert.pem .
COPY key.pem .

# Install the dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && python -m spacy download en_core_web_sm \
    && python -m spacy link en_core_web_sm en

# Copy the rest of your application into the container
COPY . .

# Expose the port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--ssl-keyfile", "key.pem", "--ssl-certfile", "cert.pem"]