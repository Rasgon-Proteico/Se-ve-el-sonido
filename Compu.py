import pyaudio
import numpy as np
import serial
import time

# --- Configuración del puerto serie ---
try:
    ser = serial.Serial('COM5', 115200, timeout=1) # Asegúrate de que este es el puerto correcto
    print(f"Conectado a {ser.name}")
    time.sleep(2) # Darle tiempo al ESP32 para que se reinicie
except serial.SerialException:
    print("Error: No se pudo abrir el puerto serie. Verifica el puerto y la conexión.")
    exit()

# --- Configuración de audio ---
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024 * 2

# --- Configuración del espectro ---
NUM_BINS = 32

p = pyaudio.PyAudio()

stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK
)

print("Iniciando analizador de espectro...")

try:
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False) # Evitar errores si la PC va lenta
        numpy_data = np.frombuffer(data, dtype=np.int16)

        fft_data = np.fft.rfft(numpy_data)
        fft_magnitude = np.abs(fft_data)

        bin_size = len(fft_magnitude) // NUM_BINS
        binned_magnitudes = []
        for i in range(NUM_BINS):
            bin_value = np.max(fft_magnitude[i * bin_size : (i + 1) * bin_size])
            binned_magnitudes.append(bin_value)
        
        # Escala logarítmica
        scaled_values = np.log10(np.array(binned_magnitudes) + 1e-10) * 10
        
      # Escala logarítmica
        log_values = np.log10(np.array(binned_magnitudes) + 1e-10) * 10

# --- AÑADE ESTA LÍNEA DE DIAGNÓSTICO ---
        print(f"Valores LOG (antes de escalar): {[f'{v:.1f}' for v in log_values]}")

# ===> ÁREA DE AJUSTE PRINCIPAL <===
        min_log_val = 10.0
        max_log_val = 50.0 # <- Intenta subir este número MUCHO MÁS, ej: 10.0 o 12.0
        scaled_values = np.interp(log_values, [min_log_val, max_log_val], [0, 63])
# ====================================

        scaled_values = np.clip(scaled_values, 0, 63).astype(int)

# Imprimir para diagnóstico final
        print(f"Valores FINALES: {scaled_values}")
        data_string = ",".join(map(str, scaled_values)) + "\n"
        ser.write(data_string.encode())
        
        time.sleep(0.01)

except KeyboardInterrupt:
    print("Deteniendo...")

finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
    ser.close()
    print("Conexiones cerradas.")