from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        # Capture the query name or fall back safely to 'Developer'
        user_name = query_params.get('name', ['Developer'])[0]

        # 🛠️ SERVERLESS PATH RESOLUTION FIX:
        # __file__ gives us: /var/task/api/index.py
        # os.path.dirname(__file__) gives us the folder: /var/task/api
        current_dir = os.path.dirname(__file__)
        
        # Move up one level out of 'api' and point directly into 'templates/dashboard.html'
        template_path = os.path.abspath(os.path.join(current_dir, '..', 'templates', 'dashboard.html'))

        try:
            # Open and read the raw template markup content string
            with open(template_path, 'r', encoding='utf-8') as file:
                html_template = file.read()
            
            # Dynamically inject your values by swapping out your token wrappers
            rendered_html = html_template.replace('{{name}}', user_name)

            # Return the successfully compiled HTML page
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=UTF-8')
            self.end_headers()
            self.wfile.write(rendered_html.encode('utf-8'))
            return

        except FileNotFoundError:
            # Fallback error catch layout if the deployment script paths split or disconnect
            self.send_response(444)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            error_message = f"Error: Template asset not found at absolute routing location:\n{template_path}"
            self.wfile.write(error_message.encode('utf-8'))
            return
