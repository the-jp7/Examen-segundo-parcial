FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Config de ssh: "ssh hadoop@hadoop" usa la llave compartida
RUN mkdir -p /root/.ssh \
    && printf 'Host hadoop\n  User hadoop\n  IdentityFile /keys/id_ed25519\n  StrictHostKeyChecking no\n  UserKnownHostsFile /dev/null\n' > /root/.ssh/config \
    && chmod 600 /root/.ssh/config

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
CMD ["python", "app.py"]