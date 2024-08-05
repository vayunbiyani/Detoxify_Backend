FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .
# Link the model in the container

RUN python -m spacy link /app/spacy_model/en_core_web_sm en_core_web_sm

# Install the dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of your application into the container
COPY . .

# Expose the port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
