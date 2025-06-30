"""Launch the web and thought servers simultaneously."""

from threading import Thread
from .web.server import app as web_app
from .thought_server import app as thought_app


def run_web() -> None:
    """Run the Flask web server without the reloader."""
    web_app.run(debug=True, use_reloader=False)


def run_thought() -> None:
    """Run the local thought API without the reloader."""
    thought_app.run(host="0.0.0.0", port=8080, use_reloader=False)


def main():
    t1 = Thread(target=run_web, daemon=True)
    t2 = Thread(target=run_thought, daemon=True)
    t1.start()
    t2.start()
    try:
        t1.join()
        t2.join()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
