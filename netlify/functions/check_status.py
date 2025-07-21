import json
import requests
import time
from datetime import datetime

def handler(event, context):
    """
    Función Lambda que verifica el estado de una URL.
    Recibe la URL del frontend y devuelve los resultados.
    """
    try:
        # Los datos del cuerpo de la solicitud están en event['body']
        # y vienen como un string JSON, así que hay que parsearlos.
        body = json.loads(event['body'])
        url = body.get('url')

        if not url:
            return {
                'statusCode': 400,
                'headers': { 'Content-Type': 'application/json' },
                'body': json.dumps({ 'message': 'URL no proporcionada en el cuerpo de la solicitud.' })
            }

        result_messages = []
        result_messages.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Verificando: {url}\n")

        try:
            start_time = time.time()
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, timeout=10, headers=headers)
            end_time = time.time()
            response_time = (end_time - start_time) * 1000 # Convertir a milisegundos

            result_messages.append(f"Estado HTTP: {response.status_code}\n")
            result_messages.append(f"Tiempo de respuesta: {response_time:.2f} ms\n")

            if response.status_code == 200:
                result_messages.append("Estado: ✅ ¡Accesible! El servidor respondió correctamente.\n")
                if response_time < 500:
                    result_messages.append("Velocidad: ⚡️ ¡Rápida! El servidor responde muy bien.\n")
                    conclusion = "¡Estupendo! Es muy probable que puedas realizar tu examen sin problemas de conexión por parte del servidor."
                elif 500 <= response_time < 2000:
                    result_messages.append("Velocidad: 🐢 Aceptable. Podría estar un poco lento en horas pico.\n")
                    conclusion = "Podrías realizar tu examen, pero la experiencia podría ser un poco lenta. Considera la hora."
                else:
                    result_messages.append("Velocidad: 🐌 ¡Lenta! El servidor está tardando mucho en responder.\n")
                    conclusion = "¡Advertencia! El servidor está muy lento. No se recomienda intentar el examen en este momento, podrías tener interrupciones."
                result_messages.append(f"\nConclusión: {conclusion}\n")

            elif 500 <= response.status_code < 600:
                result_messages.append(f"Estado: ❌ ¡Problema en el servidor! Código de error {response.status_code}.\n")
                result_messages.append("Conclusión: **¡ALERTA!** 🚨 Es muy probable que el servidor esté caído o tenga problemas graves.\n")
                result_messages.append("Definitivamente **NO se recomienda** intentar el examen ahora mismo.\n")
            elif 400 <= response.status_code < 500:
                result_messages.append(f"Estado: 🟠 Problema del cliente o recurso no encontrado. Código de error {response.status_code}.\n")
                result_messages.append("Conclusión: El servidor respondió, pero con un error. Revisa la URL ingresada. Puede que la página específica no exista.\n")
            else:
                result_messages.append(f"Estado: ❓ Código de estado desconocido o inusual: {response.status_code}.\n")
                result_messages.append("Conclusión: Podría haber un problema inesperado. Monitorea o contacta soporte técnico.\n")

        except requests.exceptions.Timeout:
            result_messages.append("Estado: 🚫 ¡Caído o muy lento! El servidor no respondió a tiempo (Timeout).\n")
            result_messages.append("Conclusión: **¡CRÍTICO!** 🔴 Es muy probable que el servidor esté caído o inaccesible.\n")
            result_messages.append("Absolutamente **NO se recomienda** intentar el examen en este momento.\n")
        except requests.exceptions.ConnectionError:
            result_messages.append("Estado: 🔌 ¡Caído o inaccesible! Error de conexión.\n")
            result_messages.append("Conclusión: **¡CRÍTICO!** 🔴 El servidor parece no estar disponible o no se pudo establecer una conexión.\n")
            result_messages.append("Absolutamente **NO se recomienda** intentar el examen en este momento.\n")
        except Exception as e:
            result_messages.append(f"Ocurrió un error inesperado: {e}\n")
            result_messages.append("Conclusión: ⚠️ No se pudo verificar el estado correctamente. Revisa el error o la URL.\n")

        return {
            'statusCode': 200,
            'headers': { 'Content-Type': 'application/json' },
            'body': json.dumps({ 'result': "".join(result_messages) })
        }

    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': { 'Content-Type': 'application/json' },
            'body': json.dumps({ 'message': 'Cuerpo de la solicitud JSON inválido.' })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': { 'Content-Type': 'application/json' },
            'body': json.dumps({ 'message': f'Error interno del servidor: {str(e)}' })
        }