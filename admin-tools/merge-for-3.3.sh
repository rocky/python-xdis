#/bin/bash
cd $(dirname ${BASH_SOURCE[0]})
if . ./setup-python-3.3.sh; then
    git merge python-3.6-to-3.10
fi
