#!/bin/bash

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

cat << EOF
Now you can run tests.
$ tox
EOF
