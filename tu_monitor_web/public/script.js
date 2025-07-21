document.addEventListener('DOMContentLoaded', () => {
    const urlInput = document.getElementById('urlInput');
    const checkButton = document.getElementById('checkButton');
    const resultsOutput = document.getElementById('resultsOutput');

    checkButton.addEventListener('click', async () => {
        const url = urlInput.value.trim();
        if (!url) {
            resultsOutput.textContent = "⚠️ Por favor, ingresa una URL o dirección IP.";
            return;
        }

        resultsOutput.textContent = `⏳ Verificando: ${url}\nPor favor, espera...`;
        checkButton.disabled = true; // Deshabilitar botón
        checkButton.textContent = "Verificando... ⏳";

        try {
            // Llama a tu función serverless de Netlify
            // La ruta es /.netlify/functions/nombre_de_tu_funcion
            const response = await fetch('/.netlify/functions/check_status', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`Error del servidor (${response.status}): ${errorData.message || response.statusText}`);
            }

            const data = await response.json();
            resultsOutput.textContent = data.result; // Mostrar el resultado del backend
        } catch (error) {
            resultsOutput.textContent = `❌ Error al conectar con el servicio: ${error.message}\n` +
                                        `Asegúrate que la URL es correcta y que la función Netlify está desplegada.`;
            console.error('Error al verificar el estado:', error);
        } finally {
            checkButton.disabled = false; // Habilitar botón
            checkButton.textContent = "Verificar Estado ✨";
        }
    });
});