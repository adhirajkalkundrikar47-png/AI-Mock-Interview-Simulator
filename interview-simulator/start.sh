#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
mkdir -p build
java com.sun.tools.javac.Main --release 17 -d build src/main/java/com/interview/*.java
java -cp build com.interview.LocalServer
