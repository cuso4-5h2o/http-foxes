import http.server
import socketserver
import os
import yaml

Handler = http.server.SimpleHTTPRequestHandler


def load_config():
    with open(os.path.join(os.getcwd(), "config.yaml"), "r") as config_file:
        return yaml.safe_load(config_file)


config = load_config()
publish_dir = os.path.join(os.getcwd(), config["publish_dir"])

with socketserver.TCPServer(("", config["test_server_port"]), Handler) as httpd:
    os.chdir(publish_dir)
    print("Listening on port", config["test_server_port"])
    httpd.serve_forever()
