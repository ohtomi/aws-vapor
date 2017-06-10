#!/bin/bash

function usage() {
    cat << EOF
Usage: $0 [prepare|run]
EOF
}

function prepare() {
    for i in 3.6.1 3.5.3 3.4.6 2.7.13
    do
        pyenv install $i
    done

    cat << EOF > ~/.pyenv/version
system
3.6.1
3.5.3
3.4.6
2.7.13
EOF
}

function run() {
    tox
}

case "$1" in
    "prepare")
        prepare
        ;;
    "run")
        run
        ;;
    *)
        usage
        exit 1
        ;;
esac
