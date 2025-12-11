import pyodbc
import random
from datetime import datetime

# Configuración de la base de datos
SERVER = r'ALANLCQ\SQLEXPRESS'
DATABASE = 'JuegoBatallas'
TABLE = 'Batallas'

# Configuración del juego
PLAYER_MAX_HP = 100
ENEMY_MAX_HP = 80
PLAYER_ATTACK_MIN = 15
PLAYER_ATTACK_MAX = 25
ENEMY_ATTACK_MIN = 10
ENEMY_ATTACK_MAX = 20
HEAL_AMOUNT = 20
DEFEND_REDUCTION = 0.5


def conectar_bd():
    """Establece conexión con SQL Server."""
    try:
        connection_string = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={r'ALANLCQ\SQLEXPRESS'};'
            f'DATABASE={r'JuegoBatallas'};'
            f'Trusted_Connection=yes;'
        )
        conn = pyodbc.connect(connection_string)
        return conn
    except pyodbc.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None


def crear_tabla_si_no_existe():
    """Crea la tabla Batallas si no existe."""
    conn = conectar_bd()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(f'''
                IF NOT EXISTS (SELECT * FROM sys.objects 
                              WHERE object_id = OBJECT_ID(N'[dbo].[{TABLE}]') 
                              AND type in (N'U'))
                CREATE TABLE {TABLE} (
                    Id INT IDENTITY(1,1) PRIMARY KEY,
                    Jugador VARCHAR(50) NOT NULL,
                    Enemigo VARCHAR(50) NOT NULL,
                    DanioTotal INT NOT NULL,
                    Ganador VARCHAR(50) NOT NULL,
                    Fecha DATETIME NOT NULL
                )
            ''')
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except pyodbc.Error as e:
            print(f"Error al crear la tabla: {e}")
            conn.close()
            return False
    return False


def insertar_batalla(jugador, enemigo, danio_total, ganador, fecha):
    """Inserta los resultados de una batalla en la base de datos."""
    conn = conectar_bd()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(f'''
                INSERT INTO {TABLE} (Jugador, Enemigo, DanioTotal, Ganador, Fecha)
                VALUES (?, ?, ?, ?, ?)
            ''', (jugador, enemigo, danio_total, ganador, fecha))
            conn.commit()
            cursor.close()
            conn.close()
            print(f"\n✓ Batalla guardada en la base de datos.")
            return True
        except pyodbc.Error as e:
            print(f"Error al insertar batalla: {e}")
            conn.close()
            return False
    return False


def mostrar_estado(jugador_hp, enemigo_hp, jugador_max_hp, enemigo_max_hp):
    """Muestra el estado actual de ambos combatientes."""
    print("\n" + "="*50)
    print(f"JUGADOR: {jugador_hp}/{jugador_max_hp} HP")
    print(f"ENEMIGO: {enemigo_hp}/{enemigo_max_hp} HP")
    print("="*50)


def atacar_jugador(enemigo_hp, danio_min, danio_max):
    """El jugador ataca al enemigo."""
    danio = random.randint(danio_min, danio_max)
    nuevo_hp = max(0, enemigo_hp - danio)
    print(f"\n⚔️ ¡Ataque del jugador! Causa {danio} de daño.")
    return nuevo_hp, danio


def defender_jugador():
    """El jugador se defiende, reduciendo el próximo daño."""
    print("\n🛡️ El jugador se defiende. El próximo ataque recibirá menos daño.")
    return True


def curar_jugador(jugador_hp, jugador_max_hp, cantidad_curacion):
    """El jugador se cura."""
    hp_anterior = jugador_hp
    nuevo_hp = min(jugador_max_hp, jugador_hp + cantidad_curacion)
    curacion_real = nuevo_hp - hp_anterior
    print(f"\n💚 El jugador se cura {curacion_real} HP.")
    return nuevo_hp


def atacar_enemigo(jugador_hp, danio_min, danio_max, defendiendo=False):
    """El enemigo ataca al jugador."""
    danio = random.randint(danio_min, danio_max)
    if defendiendo:
        danio = int(danio * DEFEND_REDUCTION)
        print(f"\n⚔️ El enemigo ataca! Pero el jugador se defiende. Recibes {danio} de daño.")
    else:
        print(f"\n⚔️ ¡Ataque del enemigo! Causa {danio} de daño.")
    nuevo_hp = max(0, jugador_hp - danio)
    return nuevo_hp, danio


def accion_enemigo():
    """Determina la acción aleatoria del enemigo."""
    acciones = ['atacar', 'atacar', 'atacar']  # Mayor probabilidad de atacar
    return random.choice(acciones)


def menu_jugador():
    """Muestra el menú de acciones del jugador."""
    print("\n--- TURNO DEL JUGADOR ---")
    print("1. Atacar")
    print("2. Defender")
    print("3. Curar")
    while True:
        try:
            opcion = input("Elige tu acción (1-3): ")
            if opcion in ['1', '2', '3']:
                return opcion
            else:
                print("Opción inválida. Elige 1, 2 o 3.")
        except ValueError:
            print("Entrada inválida. Elige 1, 2 o 3.")


def batalla():
    """Función principal que ejecuta la batalla."""
    print("\n" + "="*50)
    print("🎮 JUEGO DE BATALLAS 🎮")
    print("="*50)
    
    # Nombres de los combatientes
    nombre_jugador = input("\nIngresa el nombre del jugador: ").strip() or "Jugador"
    nombre_enemigo = input("Ingresa el nombre del enemigo: ").strip() or "Enemigo"
    
    # Inicializar estadísticas
    jugador_hp = PLAYER_MAX_HP
    enemigo_hp = ENEMY_MAX_HP
    danio_total_jugador = 0
    danio_total_enemigo = 0
    defendiendo = False
    
    print(f"\n¡La batalla comienza! {nombre_jugador} vs {nombre_enemigo}")
    
    turno = 1
    
    # Bucle principal de batalla
    while jugador_hp > 0 and enemigo_hp > 0:
        print(f"\n\n--- TURNO {turno} ---")
        mostrar_estado(jugador_hp, enemigo_hp, PLAYER_MAX_HP, ENEMY_MAX_HP)
        
        # Turno del jugador
        accion = menu_jugador()
        defendiendo = False
        
        if accion == '1':  # Atacar
            enemigo_hp, danio = atacar_jugador(enemigo_hp, PLAYER_ATTACK_MIN, PLAYER_ATTACK_MAX)
            danio_total_jugador += danio
        elif accion == '2':  # Defender
            defender_jugador()
            defendiendo = True
        elif accion == '3':  # Curar
            jugador_hp = curar_jugador(jugador_hp, PLAYER_MAX_HP, HEAL_AMOUNT)
        
        # Verificar si el enemigo fue derrotado
        if enemigo_hp <= 0:
            print(f"\n💀 ¡{nombre_enemigo} ha sido derrotado!")
            break
        
        # Turno del enemigo
        print("\n--- TURNO DEL ENEMIGO ---")
        accion_enem = accion_enemigo()
        
        if accion_enem == 'atacar':
            jugador_hp, danio = atacar_enemigo(
                jugador_hp, ENEMY_ATTACK_MIN, ENEMY_ATTACK_MAX, defendiendo
            )
            danio_total_enemigo += danio
        
        # Verificar si el jugador fue derrotado
        if jugador_hp <= 0:
            print(f"\n💀 ¡{nombre_jugador} ha sido derrotado!")
            break
        
        defendiendo = False  # Reset defensa después del turno del enemigo
        turno += 1
    
    # Resultado final
    mostrar_estado(jugador_hp, enemigo_hp, PLAYER_MAX_HP, ENEMY_MAX_HP)
    
    if jugador_hp > 0:
        ganador = nombre_jugador
        print(f"\n🏆 ¡VICTORIA! {nombre_jugador} gana la batalla!")
    else:
        ganador = nombre_enemigo
        print(f"\n💀 DERROTA. {nombre_enemigo} gana la batalla.")
    
    danio_total = danio_total_jugador + danio_total_enemigo
    
    # Guardar en base de datos
    fecha_batalla = datetime.now()
    insertar_batalla(nombre_jugador, nombre_enemigo, danio_total, ganador, fecha_batalla)
    
    print(f"\n📊 Estadísticas de la batalla:")
    print(f"   Daño total causado: {danio_total}")
    print(f"   Daño del jugador: {danio_total_jugador}")
    print(f"   Daño del enemigo: {danio_total_enemigo}")
    print(f"   Turnos totales: {turno}")


def main():
    """Función principal del programa."""
    print("\nInicializando juego...")
    
    # Crear tabla si no existe
    if crear_tabla_si_no_existe():
        print("✓ Base de datos lista.")
    else:
        print("⚠️ Advertencia: No se pudo conectar a la base de datos.")
        print("El juego continuará, pero no se guardarán las batallas.")
    
    jugar = True
    
    while jugar:
        batalla()
        
        respuesta = input("\n¿Deseas jugar otra batalla? (s/n): ").strip().lower()
        if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
            jugar = False
    
    print("\n¡Gracias por jugar! 👋")


if __name__ == "__main__":
    main()

    