FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        openjdk-17-jdk-headless \
        python3 \
        curl \
        ca-certificates \
        procps \
        openssh-server \
        openssh-client \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV HADOOP_VERSION=3.4.1
ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

RUN curl -fsSL https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz \
        | tar -xz -C /opt \
    && mv /opt/hadoop-${HADOOP_VERSION} ${HADOOP_HOME}

# --- SSH ---
# Usuario sin contraseña (solo entra con llave)
RUN useradd -m -s /bin/bash hadoop \
    && mkdir -p /run/sshd \
    && ssh-keygen -A \
    && mkdir -p /home/hadoop/.ssh \
    && ssh-keygen -t ed25519 -N "" -f /home/hadoop/.ssh/id_ed25519 \
    && cat /home/hadoop/.ssh/id_ed25519.pub >> /home/hadoop/.ssh/authorized_keys \
    && printf 'Host *\n  StrictHostKeyChecking accept-new\n' > /home/hadoop/.ssh/config \
    && chmod 700 /home/hadoop/.ssh \
    && chmod 600 /home/hadoop/.ssh/authorized_keys /home/hadoop/.ssh/id_ed25519 /home/hadoop/.ssh/config \
    && chown -R hadoop:hadoop /home/hadoop/.ssh \
    && sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config \
    && sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config

# Variables visibles también en sesiones ssh no interactivas
RUN printf 'JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64\nHADOOP_HOME=/opt/hadoop\nPATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/hadoop/bin:/opt/hadoop/sbin\n' >> /etc/environment

# Script de arranque: comparte la llave privada y levanta sshd
RUN printf '#!/bin/bash\nset -e\nmkdir -p /keys\ncp /home/hadoop/.ssh/id_ed25519 /keys/id_ed25519\nchmod 600 /keys/id_ed25519\nexec /usr/sbin/sshd -D -e\n' > /entrypoint.sh \
    && chmod +x /entrypoint.sh

EXPOSE 22
WORKDIR /opt/hadoop
ENTRYPOINT ["/entrypoint.sh"]