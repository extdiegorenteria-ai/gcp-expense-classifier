import os
import subprocess
import time
from PIL import Image, ImageDraw, ImageFont

def create_receipt_image(output_path: str):
    width, height = 450, 600
    image = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Dibujar líneas del ticket
    draw.text((80, 40), "RESTAURANTE EL BUEN SABOR", fill=(0, 0, 0))
    draw.text((150, 70), "RUC: 20456789123", fill=(50, 50, 50))
    draw.text((120, 95), "BOLETA ELECTRONICA", fill=(50, 50, 50))
    draw.line([(30, 130), (420, 130)], fill=(180, 180, 180), width=2)

    draw.text((40, 150), "FECHA: 2026-09-18", fill=(0, 0, 0))
    draw.text((40, 175), "HORA: 13:45", fill=(0, 0, 0))
    draw.line([(30, 210), (420, 210)], fill=(180, 180, 180), width=1)

    draw.text((40, 230), "1x Menu Ejecutivo ........... S/ 35.00", fill=(0, 0, 0))
    draw.text((40, 260), "1x Bebida Natural ........... S/ 10.00", fill=(0, 0, 0))
    draw.line([(30, 310), (420, 310)], fill=(180, 180, 180), width=2)

    draw.text((40, 340), "SUBTOTAL:      PEN  38.14", fill=(50, 50, 50))
    draw.text((40, 370), "IGV (18%):     PEN   6.86", fill=(50, 50, 50))
    draw.text((40, 410), "TOTAL A PAGAR: PEN  45.00", fill=(0, 0, 0))

    draw.line([(30, 460), (420, 460)], fill=(180, 180, 180), width=1)
    draw.text((110, 490), "GRACIAS POR SU PREFERENCIA", fill=(80, 80, 80))

    image.save(output_path, "JPEG", quality=95)
    print(f"Ticket de prueba generado en: {output_path}")

if __name__ == "__main__":
    test_img = os.path.abspath("tests/sample_ticket.jpg")
    create_receipt_image(test_img)
