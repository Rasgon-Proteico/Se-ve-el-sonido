# main.py -- put your code here!
from machine import Pin, I2C
import sh1106 # Importamos el driver
import sys
import time

# --- Configuración de la pantalla ---
# Pines I2C (ajusta si usas otros)
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

# Dimensiones de la pantalla
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64
display = sh1106.SH1106_I2C(SCREEN_WIDTH, SCREEN_HEIGHT, i2c,rotate=180)

# Limpiamos la pantalla al inicio
display.fill(0)
display.show()

# --- Configuración del espectro ---
NUM_BINS = 32 # Debe coincidir con el script de la PC
BAR_WIDTH = SCREEN_WIDTH // NUM_BINS # Ancho de cada barra

print("Esperando datos desde la PC por el puerto serie...")
print()
display.text('Esperando...', 0, 0, 1)
display.show()

# --- Bucle principal en el ESP32 ---
while True:
    input_data = sys.stdin.readline()

    if input_data:
        try:
            # Limpiar la cadena ANTES de comprobar si está vacía
            clean_data = input_data.strip()
            
            # Si la cadena, después de limpiarla, no está vacía, la procesamos.
            if clean_data: 
                # Separar los valores por la coma y convertirlos a enteros
                magnitudes = [int(v) for v in clean_data.split(',')]

                # Verificar si recibimos la cantidad correcta de datos
                if len(magnitudes) == NUM_BINS:
                    # (El resto del código de dibujo es correcto y no cambia)
                    display.fill(0) 

                    for i, mag in enumerate(magnitudes):
                        x = i * BAR_WIDTH
                        y = SCREEN_HEIGHT - mag 
                        w = BAR_WIDTH - 1 
                        h = mag
                        display.fill_rect(x, y, w, h, 1)

                    display.show()

        except (ValueError, IndexError) as e:
            # Ahora este error debería ocurrir mucho menos, o nunca.
            print(f"Error al procesar datos: {e}, Data: '{input_data}'")
            pass