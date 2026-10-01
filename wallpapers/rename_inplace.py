import os
import sys

# Forzar UTF-8 en consola Windows para nombres con caracteres especiales
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

# Carpeta donde está este script (wallpapers)
BASE = os.path.dirname(os.path.abspath(__file__))
PREFIJO_RAIZ = "pic_"
EXCLUIR_DIRS = {"live", "__pycache__"}
EXTENSIONES_VALIDAS = ('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff')
TEMP_PREFIJO = "__tmp_rename__"


def recolectar_carpetas():
    """Devuelve lista de (dir_actual, prefijo, [imagenes]) sin tocar nada."""
    carpetas = []
    for dir_actual, subdirs, archivos in os.walk(BASE, topdown=True):
        # Excluir carpeta live (y todo lo que cuelgue de ella)
        subdirs[:] = [d for d in subdirs if d not in EXCLUIR_DIRS]
        if os.path.basename(dir_actual) in EXCLUIR_DIRS:
            continue

        if os.path.abspath(dir_actual) == os.path.abspath(BASE):
            prefijo = PREFIJO_RAIZ
        else:
            prefijo = f"{os.path.basename(dir_actual)}_"

        imagenes = sorted([f for f in archivos if f.lower().endswith(EXTENSIONES_VALIDAS)])
        carpetas.append((dir_actual, prefijo, imagenes))
    return carpetas


def renombrar_inplace(dry_run=False):
    carpetas = recolectar_carpetas()
    total_antes = sum(len(imgs) for _, _, imgs in carpetas)
    print(f"Carpetas a procesar: {len(carpetas)} | Imágenes totales: {total_antes}")
    for dir_actual, prefijo, _ in carpetas:
        rel = os.path.relpath(dir_actual, BASE)
        print(f" - {rel} -> prefijo '{prefijo}'")

    if dry_run:
        print("\n[DRY-RUN] No se renombró nada.")
        return

    total_despues = 0
    for dir_actual, prefijo, imagenes in carpetas:
        if not imagenes:
            continue

        # Fase 1: pasar todo a nombres temporales únicos para evitar
        # colisiones (ej. pic_1.jpg ya existe y sería sobreescrito).
        temporales = []
        for i, nombre in enumerate(imagenes):
            _, ext = os.path.splitext(nombre)
            tmp_nombre = f"{TEMP_PREFIJO}{i}{ext.lower()}"
            src = os.path.join(dir_actual, nombre)
            tmp = os.path.join(dir_actual, tmp_nombre)
            os.rename(src, tmp)
            temporales.append(tmp_nombre)

        # Fase 2: temporales -> nombre final secuencial
        contador = 1
        for tmp_nombre in sorted(temporales):
            _, ext = os.path.splitext(tmp_nombre)
            nuevo_nombre = f"{prefijo}{contador}{ext.lower()}"
            src = os.path.join(dir_actual, tmp_nombre)
            dst = os.path.join(dir_actual, nuevo_nombre)
            os.rename(src, dst)
            rel = os.path.relpath(dir_actual, BASE)
            print(f"Renombrado: {os.path.join(rel, tmp_nombre)} -> {nuevo_nombre}")
            contador += 1
            total_despues += 1

    print(f"\n¡Terminado! Antes: {total_antes} | Después: {total_despues}")
    if total_antes != total_despues:
        print("ADVERTENCIA: la cantidad cambió, revisa errores.")
    else:
        print("Cantidad intacta, misma cantidad de wallpapers.")


if __name__ == "__main__":
    # Uso: python renombrar_inplace.py         -> renombra de verdad
    #      python renombrar_inplace.py --dry-run -> solo muestra lo que haría
    dry = "--dry-run" in sys.argv
    renombrar_inplace(dry_run=dry)
