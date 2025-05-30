import http.server
import json
from urllib.parse import urlparse, parse_qs

stored_offer = None
stored_answer = None
stored_offerer_ice_candidates = []
stored_answerer_ice_candidates = []

class SignalingHandler(http.server.BaseHTTPRequestHandler):
    def set_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.set_cors_headers()
        self.end_headers()

    def do_POST(self):
        self.send_response(200)
        self.set_cors_headers()  # Add CORS headers to POST requests
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError as e:
            self.send_error(400, f"Invalid JSON: {e}")
            return

        path = urlparse(self.path).path

        if path == '/offer':
            global stored_offer
            stored_offer = data
            print("Received offer:", json.dumps(stored_offer, indent=2))
            self.end_headers()
        elif path == '/answer':
            global stored_answer
            stored_answer = data
            print("Received answer:", json.dumps(stored_answer, indent=2))
            self.end_headers()
        elif path == '/offerer-ice-candidate':
            global stored_offerer_ice_candidates
            stored_offerer_ice_candidates.append(data)
            print("Received offerer ICE candidate:", json.dumps(data, indent=2))
            self.end_headers()
        elif path == '/answerer-ice-candidate':
            global stored_answerer_ice_candidates
            stored_answerer_ice_candidates.append(data)
            print("Received answerer ICE candidate:", json.dumps(data, indent=2))
            self.end_headers()
        else:
            self.send_error(404, "POST endpoint not found")

    def do_GET(self):
        self.send_response(200)
        self.set_cors_headers()  # Add CORS headers to GET requests
        path = urlparse(self.path).path

        if path == '/offer':
            if stored_offer is not None:
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(stored_offer).encode('utf-8'))
                print("Sent offer:", json.dumps(stored_offer, indent=2))
            else:
                self.send_error(404, "Offer not found")
        elif path == '/answer':
            if stored_answer is not None:
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(stored_answer).encode('utf-8'))
                print("Sent answer:", json.dumps(stored_answer, indent=2))
            else:
                self.send_error(404, "Answer not found")
        elif path == '/offerer-ice-candidates':
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(stored_offerer_ice_candidates).encode('utf-8'))
            print("Sent offerer ICE candidates:", json.dumps(stored_offerer_ice_candidates, indent=2))
            stored_offerer_ice_candidates.clear()
        elif path == '/answerer-ice-candidates':
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(stored_answerer_ice_candidates).encode('utf-8'))
            print("Sent answerer ICE candidates:", json.dumps(stored_answerer_ice_candidates, indent=2))
            stored_answerer_ice_candidates.clear()
        else:
            self.send_error(404, "GET endpoint not found")

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = http.server.HTTPServer(server_address, SignalingHandler)
    print('Signaling server running on port 8000...')
    httpd.serve_forever()
