import os
import datetime
import uuid
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Importando o seu motor de bypass que já está na pasta
try:
    from engine import BypassEngine
except ImportError:
    # Caso o motor ainda não esteja pronto, criamos uma classe de teste
    class BypassEngine:
        def process_apk(self, input_file, output_file):
            return True
    print("[!] Aviso: Engine não encontrada, usando modo simulação.")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kl_bypass_secret_2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'
CORS(app)

# Cria as pastas necessárias
os.makedirs('uploads', exist_ok=True)
os.makedirs('processed', exist_ok=True)
os.makedirs('templates', exist_ok=True)

# Instanciando o motor
engine = BypassEngine()

# --- ROTAS DO PAINEL (FRONTEND) ---

@app.route('/')
def index():
    """Rota principal que carrega o seu Dashboard"""
    return render_template('index.html')

# --- ROTAS DA API (PARA O PROCESSAMENTO) ---

@app.route('/api/v1/upload', methods=['POST'])
def upload_apk():
    """Recebe o APK para o processo de bypass"""
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "Nenhum arquivo enviado"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "Arquivo sem nome"}), 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(input_path)

    print(f"[*] [UPLOAD] Recebido: {filename}")

    try:
        # Simulando o processo de bypass para o frontend não travar
        output_filename = f"bypass_{uuid.uuid4().hex[:8]}_{filename}"
        output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)

        # Chama o seu motor real
        engine.process_apk(input_path, output_path)

        print(f"[+] [BYPASS] Concluído: {filename}")
        
        return jsonify({
            "status": "success",
            "message": "Bypass aplicado com sucesso!",
            "download_url": f"/download/{output_filename}",
            "filename": output_filename
        }), 200

    except Exception as e:
        print(f"[!] [ERRO] {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/v1/download/<filename>', methods=['GET'])
def download_apk(filename):
    """Rota para baixar o APK processado"""
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n[!] Servidor de Bypass Iniciado!")
    print(f"[!] Acesse o Painel: http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
