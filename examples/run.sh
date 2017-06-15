#!/bin/bash

echo "- configure..."
SCRIPT_DIR=$(cd $(dirname $0) && pwd)
CONTRIB_DIR="$SCRIPT_DIR/contribs"
aws-vapor config set defaults contrib ${CONTRIB_DIR}

echo "- current config"
aws-vapor config list

echo "- generating from tiny.py"
aws-vapor generate ./tiny.py --output ./outputs/tiny.json

echo "- generating from tiny.py with add_mapping.py"
aws-vapor generate ./tiny.py --recipe add_mapping --output ./outputs/tiny_with_add_mapping.json
diff ./outputs/tiny.json ./outputs/tiny_with_add_mapping.json

echo "- generating from tiny.py with replace_parameter.py"
aws-vapor generate ./tiny.py --recipe replace_parameter --output ./outputs/tiny_with_replace_parameter.json
diff ./outputs/tiny.json ./outputs/tiny_with_replace_parameter.json

echo "- generating from mongodb.py"
aws-vapor generate ./mongodb.py --output ./outputs/mongodb.json

echo "- mongodb template"
cat ./outputs/mongodb.json
