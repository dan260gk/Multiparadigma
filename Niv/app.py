from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime  # para lafecha

#para las rutas:
#esto es del tempalte, y del abort
from flask import render_template, url_for, redirect, abort

#el froms
from forms import ClienteForm

#para generar json
from flask import jsonify

#para agregar y actualizar los registros
from flask import request


app = Flask(__name__)

USER_DB='postgres'
PASS_DB = 'contrasena1234'
URL_DB='localhost'
NAME_DB='nivelacion'
FULL_URL_DB=f'postgresql://{USER_DB}:{PASS_DB}@{URL_DB}/{NAME_DB}'
app.config['SQLALCHEMY_DATABASE_URI'] = FULL_URL_DB
app.config['SECRET_KEY'] = 'nanami'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    direccion = db.Column(db.String(100), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    correo = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f"Cliente('{self.nombre}', '{self.direccion}', '{self.telefono}', '{self.correo}')"


class Pastel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    existencia = db.Column(db.Integer, nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "precio": self.precio,
            "existencia": self.existencia,
            "descripcion": self.descripcion,
        }

class Proveedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    direccion = db.Column(db.String(100), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    correo = db.Column(db.String(50), nullable=True)
    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "direccion": self.direccion,
            "telefono": self.telefono,
            "correo": self.correo,
        }

class Venta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total = db.Column(db.Float, nullable=False)
    cliente_nombre = db.Column(db.String(50), nullable=False)
    metodo_pago = db.Column(db.String(20))

    def to_dict(self):
        return {
            "id": self.id,
            "fecha": self.fecha.isoformat(),
            "total": self.total,
            "cliente_nombre": self.cliente_nombre,
            "metodo_pago":self.metodo_pago,
        }

class Inventario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha_entrada = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    pastel_nombre = db.Column(db.String(50), nullable=False)
    lote = db.Column(db.String(20))
    def to_dict(self):
        return {
            "id": self.id,
            "cantidad": self.cantidad,
            "fecha_entrada": self.fecha_entrada.isoformat(),
            "pastel_nombre": self.pastel_nombre,
            "lote":self.lote,
        }
    
#abor 404
@app.route('/404')
def error_404():
    abort(404)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

#rutas

@app.route("/", methods=['GET'])
def clientes():
    clientes = Cliente.query.all()
    return render_template('clientes.html', clientes=clientes)

@app.route("/agregar_cliente", methods=['GET', 'POST'])
def agregar_cliente():
    form = ClienteForm()

    if form.validate_on_submit():
        nuevo_cliente = Cliente(
            nombre=form.nombre.data,
            direccion=form.direccion.data,
            telefono=form.telefono.data,
            correo=form.correo.data
        )
        db.session.add(nuevo_cliente)
        db.session.commit()
        return redirect(url_for('clientes'))  

    return render_template('agregar_cliente.html', form=form)

@app.route("/cliente/<int:cliente_id>")
def ver_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    return render_template('ver_cliente.html', cliente=cliente)

@app.route("/cliente/editar/<int:cliente_id>", methods=['GET', 'POST'])
def editar_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    form = ClienteForm(obj=cliente)

    if form.validate_on_submit():
        cliente.nombre = form.nombre.data
        cliente.direccion = form.direccion.data
        cliente.telefono = form.telefono.data
        cliente.correo = form.correo.data

        db.session.commit()
        return redirect(url_for('clientes'))

    return render_template('editar_cliente.html', form=form, cliente=cliente)

@app.route("/cliente/eliminar/<int:cliente_id>")
def eliminar_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    
    db.session.delete(cliente)
    db.session.commit()
    return redirect(url_for('clientes'))

#recibir toda la informacion de 4 entidades
@app.route("/informacion", methods=['GET'])
def informacion_completa():
    ventas = Venta.query.all()
    inventarios = Inventario.query.all()
    pasteles = Pastel.query.all()
    proveedores = Proveedor.query.all()
    informacion = {
        "ventas": [venta.to_dict() for venta in ventas],
        "inventarios": [inventario.to_dict() for inventario in inventarios],
        "pasteles": [pastel.to_dict() for pastel in pasteles],
        "proveedores": [proveedor.to_dict() for proveedor in proveedores],
    }
    return jsonify(informacion)

#obtener info de un registro [de la entidad pastel, el registro se obtiene agegando el id a la ruta]
@app.route("/pastel/<int:pastel_id>")
def pastel_json(pastel_id):
    pastel = Pastel.query.get_or_404(pastel_id)
    pastel_dict = pastel.to_dict()  
    return jsonify(pastel_dict)

#actualizar y agregar registros. nota: para agregar no se debe agregar el campo ID 
@app.route("/agregar_actualizar_venta", methods=['POST'])
def agregar_actualizar_venta():
    data = request.json
    venta_id = data.get('id')

    if venta_id:
        venta = Venta.query.get_or_404(venta_id)
        venta.fecha = data.get('fecha', venta.fecha)
        venta.total = data.get('total', venta.total)
        venta.cliente_nombre = data.get('cliente_nombre', venta.cliente_nombre)
        venta.metodo_pago=data.get('metodo_pago',venta.metodo_pago)
        estado='actualizado'
    else:
        venta = Venta(
            fecha=data['fecha'],
            total=data['total'],
            cliente_nombre=data['cliente_nombre']
        )
        db.session.add(venta)
        estado='agregado'
    db.session.commit()
    return jsonify({"message": "Registro de Venta "+estado+" exitosamente"})

@app.route("/agregar_actualizar_inventario", methods=['POST'])
def agregar_actualizar_inventario():
    data = request.json
    inventario_id = data.get('id')

    if inventario_id:
        inventario = Inventario.query.get_or_404(inventario_id)
        inventario.cantidad = data.get('cantidad', inventario.cantidad)
        inventario.fecha_entrada = data.get('fecha_entrada', inventario.fecha_entrada)
        inventario.pastel_nombre = data.get('pastel_nombre', inventario.pastel_nombre)
        inventario.lote = data.get('lote',inventario.lote)
        estado='actualizado'
    else:
        inventario = Inventario(
            cantidad=data['cantidad'],
            fecha_entrada=data['fecha_entrada'],
            pastel_nombre=data['pastel_nombre']
        )
        db.session.add(inventario)
        estado='agregado'

    db.session.commit()
    return jsonify({"message": "Registro de Inventario "+estado+" exitosamente"})

@app.route("/agregar_actualizar_pastel", methods=['POST'])
def agregar_actualizar_pastel():
    data = request.json
    pastel_id = data.get('id')
    tipo=''

    if pastel_id:
        pastel = Pastel.query.get_or_404(pastel_id)
        pastel.nombre = data.get('nombre', pastel.nombre)
        pastel.precio = data.get('precio', pastel.precio)
        pastel.existencia = data.get('existencia', pastel.existencia)
        pastel.descripcion = data.get('descripcion', pastel.descripcion)
        estado='actualizado'
    else:
        pastel = Pastel(
            nombre=data['nombre'],
            precio=data['precio'],
            existencia=data['existencia'],
            descripcion=data['descripcion']
        )
        db.session.add(pastel)
        estado='agregado'

    db.session.commit()
    return jsonify({"message": "Registro de Pastel "+estado+" exitosamente"})

@app.route("/agregar_actualizar_proveedor", methods=['POST'])
def agregar_actualizar_proveedor():
    data = request.json
    proveedor_id = data.get('id')

    if proveedor_id:
        proveedor = Proveedor.query.get_or_404(proveedor_id)
        proveedor.nombre = data.get('nombre', proveedor.nombre)
        proveedor.direccion = data.get('direccion', proveedor.direccion)
        proveedor.telefono = data.get('telefono', proveedor.telefono)
        proveedor.correo = data.get('correo', proveedor.correo)
        estado='actualizado'
    else:
        proveedor = Proveedor(
            nombre=data['nombre'],
            direccion=data['direccion'],
            telefono=data['telefono'],
            correo=data['correo']
        )
        db.session.add(proveedor)
        estado='agregado'

    db.session.commit()
    return jsonify({"message": "Registro de Proveedor "+estado+" exitosamente"})

#pare eliminar mandando el id en el header
@app.route("/eliminar_pastel", methods=['DELETE'])
def eliminar_pasteo():
    pastel_id = request.headers.get('ID')

    if not pastel_id:
        return jsonify({"error": "ID no proporcionado en el encabezado"}), 400
    pastel = Pastel.query.get_or_404(pastel_id)
    db.session.delete(pastel)
    db.session.commit()

    return jsonify({"message": "Pastel eliminado exitosamente"})