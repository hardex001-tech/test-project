import socket
import threading
import time

PORTS = [445, 3389, 5900]


def serve(port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", port))
        sock.listen(1)
        while True:
            conn, _ = sock.accept()
            conn.close()


def main() -> None:
    threads = []
    for port in PORTS:
        thread = threading.Thread(target=serve, args=(port,), daemon=True)
        thread.start()
        threads.append(thread)
    print(f"Dummy targets listening on ports: {PORTS}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        return


if __name__ == "__main__":
    main()
