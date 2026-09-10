import os
import datetime
import uuid
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Importando o motor de bypass
try:
    from engine import BypassEngine
    print("[*] Engine detectada!")
except ImportError:
    class BypassEngine:
        def process_apk(self, input_file, output_file):
            return True
    print("[!] Aviso: Engine não encontrada. Usando modo simulação.")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kl_bypass_secret_2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'
CORS(app)

# Cria as pastas necessárias se não existirem
os.makedirs('uploads', exist_ok=True)
os.makedirs('processed', exist_ok=True)
os.makedirs('templates', exist_ok=True)

# Instanciando o motor
engine = BypassEngine()

# --- ROTAS DO PAINEL (FRONTEND) ---

@app.route('/')
def index():
    """Carrega a interface do seu Dashboard"""
    return render_template('index.html')

# --- ROTAS DA API (PARA O PROCESSO DE BYPASS) ---

@app.route('/api/v1/upload', methods=['POST'])
def upload_apk():
    """Recebe o APK para o processo de bypass"""
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "Nenhum arquivo enviado"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "Arquivo sem nome"}), 400

    if not file.filename.endswith('.apk'):
        return jsonify({"status": "error", "message": "O arquivo deve ser um .apk"}), 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(input_path)

    print(f"\n[!] [UPLOAD] Recebido: {filename}")

    try:
        # Gerando nome único para o arquivo de saída
        output_filename = f"bypass_{uuid.uuid4().hex[:8]}_{filename}"
        output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)

        # Chama o motor real para processar o arquivo
        print(f"[*] [ENGINE] Iniciando processamento de: {filename}")
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
    try:
        return send_from_directory(
            app.config['PROCESSED_FOLDER'], 
            filename, 
            as_attachment=True
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"\n[!] SERVIDOR KL BYPASS INICIADO!")
    print(f"[!] Acesse o Painel: http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
