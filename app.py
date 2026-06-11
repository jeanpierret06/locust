import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if url and "sslmode=" not in url:
        if "?" in url:
            url += "&sslmode=require"
        else:
            url += "?sslmode=require"
    return psycopg2.connect(url)

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Aseguramos que use la tabla 'estudiantes' que ya tienes creada en DBeaver
        cur.execute('''
            CREATE TABLE IF NOT EXISTS estudiantes (
                id SERIAL PRIMARY KEY,
                documento VARCHAR(50) UNIQUE NOT NULL,
                nombre VARCHAR(100) NOT NULL,
                correo VARCHAR(100) UNIQUE NOT NULL,
                programa VARCHAR(100) NOT NULL,
                ficha VARCHAR(50) NOT NULL,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print("Base de datos verificada e inicializada correctamente.")
    except Exception as e:
        print(f"Error en init_db: {str(e)}", file=sys.stderr)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        documento = request.form.get('documento', '').strip()
        nombre = request.form.get('nombre', '').strip()
        correo = request.form.get('correo', '').strip()
        programa = request.form.get('programa', '').strip()
        ficha = request.form.get('ficha', '').strip()

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            # Inserción apuntando exclusivamente a la tabla 'estudiantes'
            cur.execute('''
                INSERT INTO estudiantes (documento, nombre, correo, programa, ficha)
                VALUES (%s, %s, %s, %s, %s)
            ''', (documento, nombre, correo, programa, ficha))
            conn.commit()
            cur.close()
            conn.close()
        except psycopg2.errors.UniqueViolation:
            print("Aviso: El documento o correo ya existe en el sistema.", file=sys.stderr)
        except Exception as e:
            print(f"Error en inserción SQL: {str(e)}", file=sys.stderr)
            
        return redirect(url_for('registro'))

    # Consulta limpia usando RealDictCursor para alimentar la tabla embebida sin errores
    lista_estudiantes = []
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT documento, nombre, correo, programa, ficha FROM estudiantes ORDER BY id DESC;')
        lista_estudiantes = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error en consulta SQL: {str(e)}", file=sys.stderr)
    
    return render_template('registro.html', estudiantes=lista_estudiantes)

init_db()

if __name__ == '__main__':
    app.run(debug=False)