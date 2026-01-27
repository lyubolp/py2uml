lint: 
    cargo clippy

test:
    cargo test

push: lint test
    git push

# coverage: venv
#     coverage run --source="src" -m unittest discover -s tst
#     coverage report -m --fail-under 75
#     coverage lcov -o lcov.info

# run: venv
#     python3 src/main.py