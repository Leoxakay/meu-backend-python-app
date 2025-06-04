# Importa os módulos necessários do Flask e Pillow
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS # Para permitir requisições do frontend (navegador)
from PIL import Image # Biblioteca para processamento de imagens
import io # Para manipular dados em memória

# Inicializa a aplicação Flask
app = Flask(__name__)
# Habilita CORS para permitir que o frontend (rodando em um domínio diferente) se comunique com este backend
CORS(app)

# Novo endpoint para verificar o status do servidor
@app.route('/status', methods=['GET'])
def get_status():
    """
    Endpoint para verificar o status do servidor.
    Retorna um JSON indicando que o servidor está online.
    """
    return jsonify({'status': 'online'}), 200

@app.route('/convert', methods=['POST'])
def convert_image():
    """
    Endpoint para converter imagens.
    Recebe um arquivo de imagem e o formato de saída,
    e retorna a imagem convertida.
    """
    # Verifica se um arquivo foi enviado na requisição
    if 'image' not in request.files:
        return {'error': 'Nenhum arquivo de imagem fornecido'}, 400

    image_file = request.files['image']
    output_format = request.form.get('output_format')

    # Verifica se o formato de saída foi especificado
    if not output_format:
        return {'error': 'Formato de saída não especificado'}, 400

    # Verifica se o arquivo é um tipo de imagem permitido (opcional, mas boa prática)
    if not image_file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.tif', '.ico')): # Adicionado .ico para entrada
        return {'error': 'Formato de arquivo não suportado. Apenas PNG, JPG, TIFF e ICO são permitidos.'}, 400

    try:
        # Abre a imagem usando Pillow
        img = Image.open(image_file.stream)

        # Converte para o formato de saída desejado
        # Normaliza o formato para corresponder aos nomes de formato da Pillow
        if output_format.lower() == 'image/jpeg':
            fmt = 'JPEG'
        elif output_format.lower() == 'image/png':
            fmt = 'PNG'
        elif output_format.lower() == 'image/tiff':
            fmt = 'TIFF'
        elif output_format.lower() == 'image/x-icon': # Adicionado suporte para ICO
            fmt = 'ICO'
        else:
            return {'error': f'Formato de saída "{output_format}" não suportado pelo servidor.'}, 400

        # Cria um buffer de bytes em memória para salvar a imagem convertida
        img_io = io.BytesIO()
        # Para ICO, é boa prática redimensionar para um tamanho comum de ícone, como 32x32 ou 64x64
        # Pillow pode lidar com múltiplos tamanhos em um único ICO, mas para simplicidade, vamos redimensionar se for ICO
        if fmt == 'ICO':
            # Redimensiona para um tamanho comum de ícone. Pode ser ajustado.
            # Mantém a proporção e redimensiona para 64x64 como exemplo.
            img.thumbnail((64, 64), Image.Resampling.LANCZOS)
            # Para ICO, Pillow pode precisar de um modo RGB ou RGBA
            if img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGBA')
            img.save(img_io, format=fmt, sizes=[(16,16), (24,24), (32,32), (48,48), (64,64)]) # Salva múltiplos tamanhos no ICO
        else:
            img.save(img_io, format=fmt)

        img_io.seek(0) # Volta ao início do buffer

        # Retorna a imagem convertida como um arquivo
        return send_file(img_io, mimetype=output_format, as_attachment=True, download_name=f'imagem_convertida.{fmt.lower()}')

    except Exception as e:
        # Captura e retorna quaisquer erros que ocorram durante o processo
        print(f"Erro na conversão: {e}")
        return {'error': f'Erro interno do servidor durante a conversão: {str(e)}'}, 500

# Ponto de entrada para executar a aplicação Flask
if __name__ == '__main__':
    # Roda a aplicação em modo de depuração (debug=True)
    # Host '0.0.0.0' permite acesso de outras máquinas na rede, se necessário
    # Porta 5000 é a porta padrão do Flask
    app.run(debug=True, host='0.0.0.0', port=5000)
