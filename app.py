from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from werkzeug.utils import secure_filename

import os
import time
#--------------------------------------------------------------------

app = Flask(__name__)
CORS(app)

class Catalogo:
    #----------------------------------------------------------------
    # Constructor de la clase
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        self.cursor = self.conn.cursor()
        # Intentamos seleccionar la base de datos
        try:
            self.cursor.execute(f"USE {database}")
        except mysql.connector.Error as err:
            # Si la base de datos no existe, la creamos
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.cursor.execute(f"CREATE DATABASE {database}")
                self.conn.database = database
            else:
                raise err

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS noticias (
            codigo INT AUTO_INCREMENT PRIMARY KEY,
            titulo VARCHAR(100) NOT NULL,
            seccion VARCHAR(100) NOT NULL,
            descripcion VARCHAR(500) NOT NULL,            
            imagen_url VARCHAR(255))''')
        self.conn.commit()

        # '''CREATE TABLE IF NOT EXISTS productos ( notir
        #     codigo INT AUTO_INCREMENT PRIMARY KEY,
        #     descripcion VARCHAR(255) NOT NULL,
        #     cantidad INT NOT NULL,
        #     precio DECIMAL(10, 2) NOT NULL,
        #     imagen_url VARCHAR(255),
        #     proveedor INT(4))'''
        
        # Cerrar el cursor inicial y abrir uno nuevo con el parámetro dictionary=True
        self.cursor.close()
        self.cursor = self.conn.cursor(dictionary=True)

    def listar_noticias(self):
        self.cursor.execute("SELECT * FROM noticias")
        noticias = self.cursor.fetchall()
        return noticias
    
    def consultar_noticia(self, codigo):
        # Consultamos un producto a partir de su código
        self.cursor.execute(f"SELECT * FROM noticias WHERE codigo = {codigo}")
        return self.cursor.fetchone()

    def mostrar_noticia(self, codigo):
        # Mostramos los datos de un producto a partir de su código
        noticia = self.consultar_noticia(codigo)
        if noticia:
            print("-" * 40)
            print(f"Código..........: {noticia['codigo']}")
            print(f"titulo..........: {noticia['titulo']}")
            print(f"seccion.........: {noticia['seccion']}")
            print(f"descripcion.....: {noticia['descripcion']}")
            print(f"Imagen..........: {noticia['imagen_url']}")
            
            print("-" * 40)
        else:
            print("Noticia no encontrada.")

    def agregar_noticia(self, titulo, seccion, descripcion, imagen):
        sql = "INSERT INTO noticias (titulo, seccion, descripcion, imagen_url) VALUES (%s, %s, %s, %s)"
        valores = (titulo, seccion, descripcion, imagen)

        self.cursor.execute(sql,valores)
        self.conn.commit()
        return self.cursor.lastrowid

    def modificar_noticia(self, codigo, nuevo_titulo, nueva_seccion, nueva_descripcion, nueva_imagen):
        sql = "UPDATE noticias SET titulo = %s, seccion = %s, descripcion = %s, imagen_url = %s WHERE codigo = %s"
        valores = (nuevo_titulo, nueva_seccion, nueva_descripcion, nueva_imagen, codigo)

        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.rowcount > 0

    def eliminar_noticia(self, codigo):
        # Eliminamos un producto de la tabla a partir de su código
        self.cursor.execute(f"DELETE FROM noticias WHERE codigo = {codigo}")
        self.conn.commit()
        return self.cursor.rowcount > 0

#--------------------------------------------------------------------
# Cuerpo del programa
#--------------------------------------------------------------------
# Crear una instancia de la clase Catalogo
catalogo = Catalogo(host='localhost', user='root', password='', database='notir_api')

# Carpeta para guardar las imagenes
ruta_destino = './static/imagenes/'

@app.route("/noticias", methods=["GET"])
def listar_noticias():
    noticias = catalogo.listar_noticias()
    return jsonify(noticias)

@app.route("/noticias/<int:codigo>", methods=["GET"])
def mostrar_noticia(codigo):
    noticia = catalogo.consultar_noticia(codigo)
    if noticia:
        return jsonify(noticia)
    else:
        return "Noticia no encontrado", 404

@app.route("/noticias", methods=["POST"])
def agregar_noticia():
    #Recojo los datos del form
    titulo = request.form['titulo']
    seccion = request.form['seccion']
    descripcion = request.form['descripcion']
    imagen = request.files['imagen']
    
    nombre_imagen = ""

    # Genero el nombre de la imagen
    nombre_imagen = secure_filename(imagen.filename) 
    nombre_base, extension = os.path.splitext(nombre_imagen) 
    nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}" 

    nuevo_codigo = catalogo.agregar_noticia(titulo, seccion, descripcion, nombre_imagen)
    if nuevo_codigo:    
        imagen.save(os.path.join(ruta_destino, nombre_imagen))
        return jsonify({"mensaje": "Noticia agregada correctamente.", "codigo": nuevo_codigo, "imagen": nombre_imagen}), 201
    else:
        return jsonify({"mensaje": "Error al agregar la noticia."}), 500

@app.route("/noticia/<int:codigo>", methods=["PUT"])
def modificar_noticia(codigo):
    #Se recuperan los nuevos datos del formulario
    nuevo_titulo = request.form.get("titulo")
    nueva_seccion = request.form.get("seccion")
    nueva_descripcion = request.form.get("descripcion")

    
    # Verifica si se proporcionó una nueva imagen
    if 'imagen' in request.files:
        imagen = request.files['imagen']
        # Procesamiento de la imagen
        nombre_imagen = secure_filename(imagen.filename) 
        nombre_base, extension = os.path.splitext(nombre_imagen) 
        nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}" 

        # Guardar la imagen en el servidor
        imagen.save(os.path.join(ruta_destino, nombre_imagen))
        
        # Busco el producto guardado
        noticia = catalogo.consultar_noticia(codigo)
        if noticia: # Si existe el producto...
            imagen_vieja = noticia["imagen_url"]
            # Armo la ruta a la imagen
            ruta_imagen = os.path.join(ruta_destino, imagen_vieja)

            # Y si existe la borro.
            if os.path.exists(ruta_imagen):
                os.remove(ruta_imagen)
    else:     
        noticia = catalogo.consultar_noticia(codigo)
        if noticia:
            nombre_imagen = noticia["imagen_url"]

   # Se llama al método modificar_producto pasando el codigo del producto y los nuevos datos.
    if catalogo.modificar_noticia(codigo, nuevo_titulo, nueva_seccion, nueva_descripcion, nombre_imagen):
        return jsonify({"mensaje": "Noticia modificada"}), 200
    else:
        return jsonify({"mensaje": "Noticia no encontrada"}), 403

@app.route("/noticias/<int:codigo>", methods=["DELETE"])
def eliminar_noticia(codigo):
    # Primero, obtiene la información del producto para encontrar la imagen
    noticia = catalogo.consultar_noticia(codigo)
    if noticia:
        # Eliminar la imagen asociada si existe
        ruta_imagen = os.path.join(ruta_destino, noticia['imagen_url'])
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)

        # Luego, elimina el producto del catálogo
        if catalogo.eliminar_noticia(codigo):
            return jsonify({"mensaje": "Noticia eliminada"}), 200
        else:
            return jsonify({"mensaje": "Error al eliminar la noticia"}), 500
    else:
        return jsonify({"mensaje": "Noticia no encontrada"}), 404


if __name__ == "__main__":
    app.run(debug=True)