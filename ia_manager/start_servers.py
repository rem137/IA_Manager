from multiprocessing import Process
from .web.server import app as web_app
from .thought_server import app as thought_app


def run_web():
    web_app.run(debug=True)


def run_thought():
    thought_app.run(host="0.0.0.0", port=8080)


def main():
    p1 = Process(target=run_web)
    p2 = Process(target=run_thought)
    p1.start()
    p2.start()
    try:
        p1.join()
        p2.join()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
