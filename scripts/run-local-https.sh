#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
mkdir -p data
if [[ ! -f dev-keystore.p12 ]]; then
  keytool -genkeypair -alias erasmus-dev -keyalg RSA -keysize 2048 -validity 365 \
    -storetype PKCS12 -keystore dev-keystore.p12 -storepass changeit -keypass changeit \
    -dname "CN=localhost" -ext "SAN=dns:localhost,ip:127.0.0.1"
fi
export EMP_KEYSTORE="file:$(pwd)/dev-keystore.p12"
export EMP_DATABASE_URL="jdbc:h2:file:$(pwd)/data/erasmus"

java_release="${JAVA_RELEASE:-$(java -version 2>&1 | sed -n 's/.*version \"\([0-9]*\).*/\1/p' | head -1)}"
exec mvn -f src/pom.xml "-Dmaven.compiler.release=${java_release:-23}" \
  -Dspring-boot.run.profiles=https spring-boot:run
