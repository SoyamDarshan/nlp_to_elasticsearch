FROM openjdk:17-jdk-slim
WORKDIR /app

# Install Maven
RUN apt-get update && apt-get install -y maven && rm -rf /var/lib/apt/lists/*

COPY . .

# Generate Maven Wrapper if missing, then build
RUN [ -f ./mvnw ] || mvn -N io.takari:maven:wrapper
RUN ./mvnw package -DskipTests

EXPOSE 8080
CMD ["java", "-jar", "target/nlpapi-0.0.1-SNAPSHOT.jar"]
