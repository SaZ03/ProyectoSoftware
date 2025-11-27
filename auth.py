from flask_login import UserMixin
import database as db
from werkzeug.security import check_password_hash, generate_password_hash

class User(UserMixin):
    def __init__(self, id, email, nombre, id_rol):
        self.id = id
        self.email = email
        self.nombre = nombre
        self.id_rol = id_rol
    
    @staticmethod
    def get(user_id):
        query = """
        SELECT u.id_usuario, u.correo, u.nombre_usuario, r.id_rol, r.nombre_rol 
        FROM Usuario u 
        JOIN RolUsuario ru ON u.id_usuario = ru.id_usuario 
        JOIN Rol r ON ru.id_rol = r.id_rol 
        WHERE u.id_usuario = %s
        """
        result = db.execute_query(query, (user_id,), fetch=True)
        
        if result:
            user_data = result[0]
            return User(
                id=user_data['id_usuario'],
                email=user_data['correo'],
                nombre=user_data['nombre_usuario'],
                id_rol=user_data['id_rol']
            )
        return None
    
    @staticmethod
    def authenticate(email, password):
        query = "SELECT id_usuario, correo, nombre_usuario, contrasena_hash FROM Usuario WHERE correo = %s"
        result = db.execute_query(query, (email,), fetch=True)
        
        if result and result[0]:
            user_data = result[0]
            # Verificar contraseña (en producción usar check_password_hash)
            if user_data['contrasena_hash'] == password:  # Temporal - cambiar por hash real
                return User.get(user_data['id_usuario'])
        return None