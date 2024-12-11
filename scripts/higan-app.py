# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess

app = Flask(__name__)
CORS(app)

@app.route('/run-higan', methods=['POST'])
def run_higan():
    try:
        # Execute the higan-code.py script
        result = subprocess.run(['python', 'higan-code.py'], capture_output=True, text=True)
        if result.returncode != 0:
            return jsonify({"error": result.stderr}), 500
        return jsonify({"message": "Higan script executed successfully", "output": result.stdout}), 200
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
