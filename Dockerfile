# Use an Ubuntu base image with Python 3.7
FROM python:3.7-slim

# Set environment variables to avoid prompts during installations
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y tar unzip git wget libarchive13 libcurl4 libxml2\
    && rm -rf /var/lib/apt/lists/*

# # Set Python 3.7 as the default Python version
# RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1
# RUN python --version

# # Install pip for Python 3.7
# RUN python -m ensurepip --upgrade

# Set up a working directory
WORKDIR /app
COPY . .

# #scrml
# RUN apt-get install -y libarchive13 libcurl4 libxml2

RUN wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2_amd64.deb && \
    dpkg -i libssl1.1_1.1.1f-1ubuntu2_amd64.deb && \
    rm -rf libssl1.1_1.1.1f-1ubuntu2_amd64.deb

RUN wget http://131.123.42.38/lmcrs/v1.0.0/srcml_1.0.0-1_ubuntu20.04.deb && \
    dpkg -i srcml_1.0.0-1_ubuntu20.04.deb && \
    rm -rf srcml_1.0.0-1_ubuntu20.04.deb

RUN mkdir /opt/java && tar -xvzf "openlogic-openjdk-11.0.24+8-linux-x64.tar.gz" -C /opt/java 
ENV PATH="/opt/java/openlogic-openjdk-11.0.24+8-linux-x64/bin:${PATH}"

# # Install Joern v1.1.1298
# RUN wget https://github.com/joernio/joern/releases/download/v1.1.1298/joern-cli.zip \
#     && unzip joern-cli.zip -d /opt/joern \
#     && rm joern-cli.zip

# Add Joern to PATH
RUN unzip joern-cli.zip -d /opt/joern && chmod -R u+x /opt/joern/joern-cli
ENV PATH="/opt/joern/joern-cli:${PATH}"

# Verify Joern installation
# RUN joern --version

# # Expose port if Joern's server is used
# EXPOSE 8080

# Copy any necessary files into the container


# Define the default command (this can be changed as needed)
CMD ["bash"]


RUN pip install -r requirements.txt
RUN pip install -r CTG/requirements.txt




