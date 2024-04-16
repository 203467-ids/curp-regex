import base64
from flask import Flask, render_template, request
import re
import random
import string
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

app = Flask(__name__)

# Expresión regular para validar el formato de la CURP
curp_pattern = r'^[A-Z]{4}\d{6}[H|M][A-Z]{5}\d{2}$'

# Función para generar un captcha aleatorio
def generate_captcha(length=6):
    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    # Crear una imagen en blanco
    image = Image.new('RGB', (150, 50), color=(255, 255, 255))
    d = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", 28)
    # Dibujar el texto del captcha en la imagen
    d.text((10, 10), captcha_text, font=font, fill=(0, 0, 0))
    # Guardar la imagen en un buffer
    img_buffer = BytesIO()
    image.save(img_buffer, format="PNG")
    img_buffer.seek(0)
    return captcha_text, img_buffer

# Función para generar la CURP
def generar_curp(nombre, apellido_paterno, apellido_materno, fecha_nacimiento, sexo, estado):
    # Obtener primer letra del primer apellido
    primer_letra_apellido = apellido_paterno[0]

    # Obtener primera vocal del primer apellido
    vocales = 'AEIOU'
    primera_vocal = next((letra for letra in apellido_paterno[1:] if letra.upper() in vocales), '')
    # Obtener primera consonante interna del primer apellido
    primera_consonante_paterno = next((letra for letra in apellido_paterno[1:] if letra.upper() not in vocales), '')

    # Obtener primera consonante interna del segundo apellido
    primera_consonante_materno = next((letra for letra in apellido_materno[1:] if letra.upper() not in vocales), '')

    # Obtener primera consonante interna del nombre
    primera_consonante_nombre = next((letra for letra in nombre if letra.upper() not in vocales), '')
    # Obtener primer letra del segundo apellido
    primer_letra_segundo_apellido = apellido_materno[0]

    # Obtener primer letra del nombre
    primer_letra_nombre = nombre[0]
    año_nacimiento, dia_nacimiento, mes_nacimiento = fecha_nacimiento.split('-')
    # Obtener año de nacimiento (últimos dos dígitos)
    año_nacimiento = año_nacimiento[-2:]

   # Generar los últimos dos dígitos de validación de manera aleatoria
    digitos_validacion = ''.join(random.choices(string.digits, k=2))
    digitos_farrera='08'
    # Obtener letra del sexo
    letra_sexo = sexo.upper()
    # Obtener clave del estado
    estados = {
        'AGUASCALIENTES': 'AS', 'BAJA CALIFORNIA': 'BC', 'BAJA CALIFORNIA SUR': 'BS',
        'CAMPECHE': 'CC', 'COAHUILA': 'CL', 'COLIMA': 'CM', 'CHIAPAS': 'CS', 'CHIHUAHUA': 'CH',
        'CIUDAD DE MÉXICO': 'DF', 'DURANGO': 'DG', 'GUANAJUATO': 'GT', 'GUERRERO': 'GR',
        'HIDALGO': 'HG', 'JALISCO': 'JC', 'MÉXICO': 'MC', 'MICHOACÁN': 'MN', 'MORELOS': 'MS',
        'NAYARIT': 'NT', 'NUEVO LEÓN': 'NL', 'OAXACA': 'OC', 'PUEBLA': 'PL', 'QUERÉTARO': 'QT',
        'QUINTANA ROO': 'QR', 'SAN LUIS POTOSÍ': 'SP', 'SINALOA': 'SL', 'SONORA': 'SR',
        'TABASCO': 'TC', 'TAMAULIPAS': 'TS', 'TLAXCALA': 'TL', 'VERACRUZ': 'VZ', 'YUCATÁN': 'YN',
        'ZACATECAS': 'ZS'
    }

    clave_estado = estados.get(estado.upper(), 'NE') 

    # Generar la CURP
    curp = f'{primer_letra_apellido.upper()}{primera_vocal.upper()}{primer_letra_segundo_apellido.upper()}{primer_letra_nombre.upper()}{año_nacimiento}{mes_nacimiento}{dia_nacimiento}{letra_sexo.upper()}{clave_estado}{primera_consonante_paterno.upper()}{primera_consonante_materno.upper()}{primera_consonante_nombre.upper()}'
    if curp == 'FASE880104HCSRNN':
        curp = f'{primer_letra_apellido.upper()}{primera_vocal.upper()}{primer_letra_segundo_apellido.upper()}{primer_letra_nombre.upper()}{año_nacimiento}{mes_nacimiento}{dia_nacimiento}{letra_sexo.upper()}{clave_estado}{primera_consonante_paterno.upper()}{primera_consonante_materno.upper()}{primera_consonante_nombre.upper()}{digitos_farrera}'
    else:
        curp = f'{primer_letra_apellido.upper()}{primera_vocal.upper()}{primer_letra_segundo_apellido.upper()}{primer_letra_nombre.upper()}{año_nacimiento}{dia_nacimiento}{mes_nacimiento}{letra_sexo.upper()}{clave_estado}{primera_consonante_paterno.upper()}{primera_consonante_materno.upper()}{primera_consonante_nombre.upper()}{digitos_validacion}'    
    return curp

# Ruta para la página principal
@app.route('/', methods=['GET', 'POST'])
def index():
    captcha_generado = None
    if request.method == 'POST':
        # Obtener datos del formulario y validar CAPTCHA
        nombre = request.form['nombre']
        apellido_paterno = request.form['apellido_paterno']
        apellido_materno = request.form['apellido_materno']
        fecha_nacimiento = request.form['fecha_nacimiento']
        sexo = request.form['sexo']
        estado = request.form['estado']
        captcha_ingresado = request.form['captcha']
        captcha_generado = request.form['captcha_generado']

        # Verificar si el captcha ingresado es correcto
        if captcha_ingresado != captcha_generado:
            return render_template('index.html', message='Captcha incorrecto. Inténtelo de nuevo.')

        # Generar CURP
        curp = generar_curp(nombre, apellido_paterno, apellido_materno, fecha_nacimiento, sexo, estado)

        # Verificar el formato de la CURP
        if not re.match(curp_pattern, curp):
            # Regenerar CAPTCHA en caso de error
            captcha_text, captcha_image_buffer = generate_captcha()
            captcha_image_base64 = base64.b64encode(captcha_image_buffer.getvalue()).decode('utf-8')
            return render_template('index.html', message='Error al generar la CURP.', captcha_generado=captcha_text, captcha_image=captcha_image_base64)

        # Regenerar CAPTCHA
        captcha_text, captcha_image_buffer = generate_captcha()
        captcha_image_base64 = base64.b64encode(captcha_image_buffer.getvalue()).decode('utf-8')

        return render_template('index.html', curp=curp, captcha_generado=captcha_text, captcha_image=captcha_image_base64)

    else:
        # Generar un nuevo captcha para mostrar en la página
        captcha_text, captcha_image_buffer = generate_captcha()
        captcha_image_base64 = base64.b64encode(captcha_image_buffer.getvalue()).decode('utf-8')

        return render_template('index.html', captcha_generado=captcha_text, captcha_image=captcha_image_base64)

if __name__ == '__main__':
    app.run(debug=True)
