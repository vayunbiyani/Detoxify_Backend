FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the SSL files into the container
COPY ./ssl/certs/your_certificate.crt /etc/ssl/certs/
COPY ./ssl/private/your_private.key /etc/ssl/private/

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && python -m spacy download en_core_web_sm \
    && python -m spacy link en_core_web_sm en

# Copy the rest of your application into the container
COPY . .

# Expose the HTTPS port
EXPOSE 443

# Run the application with HTTPS
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "443", "--ssl-keyfile", "/etc/ssl/private/your_private.key", "--ssl-certfile", "/etc/ssl/certs/your_certificate.crt"]