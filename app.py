from core import create_app

app = create_app()

# This is the entry point. Without this, the file runs but does nothing.
if __name__ == "__main__":
    app.run(debug=True)