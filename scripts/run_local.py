import os
from app import create_app


def main():
    app = create_app("development")
    app.run(host="0.0.0.0", port=8001, debug=True)


if __name__ == "__main__":
    main()
