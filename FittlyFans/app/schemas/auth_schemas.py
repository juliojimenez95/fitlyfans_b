from marshmallow import Schema, fields, validate

class RegistroSchema(Schema):
    nombre = fields.String(required=True, validate=validate.Length(min=2, max=100))
    correo = fields.Email(required=True)
    contrasena = fields.String(required=True, validate=validate.Length(min=6, max=100))
    tipo_usuario = fields.String(required=True, validate=validate.OneOf(["entrenador", "suscriptor"]))

class LoginSchema(Schema):
    correo = fields.Email(required=True)
    contrasena = fields.String(required=True)
