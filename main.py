import uvicorn

if __name__ == "__main__":
    uvicorn.run("asgi:application", host="127.0.0.1", port=8000, log_level="debug",
                reload_dirs=["."], reload=True, reload_includes=["*.html", "*.py"])
