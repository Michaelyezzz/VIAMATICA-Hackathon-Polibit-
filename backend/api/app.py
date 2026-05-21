"""
backend/api/app.py - Aplicación Flask y rutas principales
Define los endpoints de la API conversacional
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from backend.agent.copago_agent import CopagoAgent
import traceback
from datetime import datetime, timedelta

def create_app():
    """Factory pattern para crear la aplicación Flask"""
    # Definir ruta para frontend
    root_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    frontend_path = os.path.join(root_path, 'frontend')
    
    # Crear app con static_folder y static_url_path correctos
    app = Flask(__name__)
    CORS(app)  # Habilitar CORS para frontend
    
    # Deshabilitar caché
    @app.after_request
    def set_response_headers(response):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    
    # Inicializar agente de forma perezosa para evitar fallos en el arranque
    # Se creará en la primera petición a /api/chat
    app.agent = None
    
    # Rutas
    @app.route('/', methods=['GET'])
    def index():
        """Servir frontend principal"""
        return send_from_directory(frontend_path, 'index.html', mimetype='text/html')
    
    @app.route('/styles.css', methods=['GET'])
    def serve_css():
        """Servir archivo CSS"""
        return send_from_directory(frontend_path, 'styles.css', mimetype='text/css')
    
    @app.route('/script.js', methods=['GET'])
    def serve_js():
        """Servir archivo JavaScript"""
        return send_from_directory(frontend_path, 'script.js', mimetype='application/javascript')
    
    @app.route('/health', methods=['GET'])
    def health():
        """Verificar que el servidor está activo"""
        return jsonify({"status": "ok", "message": "Servidor activo"}), 200
    
    @app.route('/api/chat', methods=['POST'])
    def chat():
        """
        Endpoint principal: recibe mensaje del usuario
        Body: {"message": "Mi síntoma..."}
        """
        try:
            data = request.json
            user_message = data.get('message', '')

            if not user_message:
                return jsonify({"error": "Mensaje vacío"}), 400

            # Inicializar agente si no existe (lazy init)
            if not getattr(app, 'agent', None):
                try:
                    app.agent = CopagoAgent()
                except Exception as e:
                    print(f"Error inicializando agente en /api/chat: {e}")
                    traceback.print_exc()
                    return jsonify({
                        "status": "error",
                        "message": "Error inicializando agente",
                        "error": str(e)
                    }), 500

            # Obtener respuesta del agente
            try:
                response = app.agent.process_message(user_message)
            except Exception as e:
                # Registrar y devolver una respuesta legible al frontend
                print(f"Error en /api/chat: {str(e)}")
                traceback.print_exc()
                fallback = (
                    "Lo siento, el servicio de LLM no está disponible en este momento. "
                    "Detalles: " + str(e)
                )
                return jsonify({
                    "status": "success",
                    "message": fallback
                }), 200

            return jsonify({
                "status": "success",
                "message": response
            }), 200

        except Exception as e:
            print(f"Error en /api/chat: {str(e)}")
            traceback.print_exc()
            return jsonify({
                "status": "error",
                "message": "Error procesando solicitud",
                "error": str(e)
            }), 500
    
    @app.route('/api/reset', methods=['POST'])
    def reset():
        """Reiniciar conversación"""
        if getattr(app, 'agent', None):
            app.agent.reset_conversation()
        else:
            # nothing to reset yet
            pass
        return jsonify({"status": "success", "message": "Conversación reiniciada"}), 200
    
    # Error handler
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Ruta no encontrada"}), 404
    
    return app