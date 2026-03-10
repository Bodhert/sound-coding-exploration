import sqlite3
import os
import sys
import urllib.parse

POSSIBLE_DB_PATHS = [
    os.path.expanduser("~/Library/Containers/org.mixxx.mixxx/Data/Library/Application Support/Mixxx/mixxxdb.sqlite")
]

def cleanup_macos_metadata(folder_path):
    """
    Elimina archivos ._* que macOS crea en discos externos.
    Estos archivos contienen metadata de recursos/atributos extendidos.
    """
    print(f"\n🧹 Limpiando archivos metadata de macOS en: {folder_path}")
    count = 0
    
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.startswith("._"):
                file_path = os.path.join(root, filename)
                try:
                    os.remove(file_path)
                    print(f"🗑️  Eliminado: {filename}")
                    count += 1
                except Exception as e:
                    print(f"❌ Error eliminando {filename}: {e}")
    
    print(f"✨ Total archivos ._* eliminados: {count}\n")
    return count

def rename_in_folder(target_folder):
    # 1. Normalizamos la ruta que tú pasas por la terminal
    target_folder = os.path.normpath(os.path.abspath(target_folder))
    
    db_path = next((p for p in POSSIBLE_DB_PATHS if os.path.exists(p)), None)
    if not db_path:
        print("❌ No se encontró la base de datos.")
        return

    try:
        # Abrir en modo lectura para no bloquear Mixxx
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.cursor()

        query = "SELECT tl.location, l.rating FROM library l JOIN track_locations tl ON l.location = tl.id WHERE l.rating > 0"
        cursor.execute(query)
        rows = cursor.fetchall()

        print(f"--- Iniciando escaneo en: {target_folder} ---")
        print(f"📁 Target folder: '{target_folder}'")
        print(f"📊 Total archivos con rating en DB: {len(rows)}\n")
        count = 0
        matched = 0

        for original_path, rating in rows:
            # LIMPIEZA CRÍTICA: Mixxx usa file:// y %20
            clean_path = original_path.replace('file://', '')
            decoded_path = urllib.parse.unquote(clean_path)
            
            # Normalizamos la ruta de la DB para que coincida con el formato de macOS
            final_path = os.path.normpath(decoded_path)

            # --- DEBUG: Si quieres ver qué está pasando, descomenta la siguiente línea:
            # print(f"Comparando: {final_path}")

            if final_path.startswith(target_folder):
                matched += 1
                print(f"✅ MATCH (rating {rating}): {final_path}")
                if not os.path.exists(final_path):
                    print(f"⚠️ El archivo existe en Mixxx pero no en el disco: {final_path}")
                    continue

                folder = os.path.dirname(final_path)
                filename = os.path.basename(final_path)
                
                # Detectar si tiene un prefijo de rating existente (XX_ o XX-)
                import re
                rating_pattern = r'^(\d{2})([-_])'
                match = re.match(rating_pattern, filename)
                
                if match:
                    existing_rating = match.group(1)
                    separator = match.group(2)  # Preservar el separador original (- o _)
                    
                    if existing_rating == "00":
                        # Reemplazar 00 con el rating de Mixxx, manteniendo el separador
                        new_filename = f"{rating:02d}{separator}{filename[3:]}"
                        new_path = os.path.join(folder, new_filename)
                        try:
                            os.rename(final_path, new_path)
                            print(f"✅ REEMPLAZADO 00{separator} → {rating:02d}{separator}: {new_filename}")
                            count += 1
                        except Exception as e:
                            print(f"❌ Error: {e}")
                    else:
                        # Ya tiene un rating diferente, no tocar
                        print(f"ℹ️ Ya tiene rating {existing_rating}{separator}: {filename}")
                else:
                    # No tiene prefijo, agregar el rating con guion bajo
                    new_path = os.path.join(folder, f"{rating:02d}_{filename}")
                    try:
                        os.rename(final_path, new_path)
                        print(f"✅ AGREGADO {rating:02d}_: {rating:02d}_{filename}")
                        count += 1
                    except Exception as e:
                        print(f"❌ Error: {e}")
            else:
                print(f"⏭️ NO MATCH: {final_path}")

        conn.close()
        print(f"\n✨ Proceso finalizado.")
        print(f"📊 Archivos que coinciden con la carpeta: {matched}")
        print(f"✅ Total renombrados: {count}")
        
        # Limpiar archivos metadata de macOS
        cleanup_macos_metadata(target_folder)

    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    rename_in_folder(folder)
