from flask_login import UserMixin
import database as db

class User(UserMixin):
    def __init__(self, id, email, nombre, id_rol, nombre_rol):
        self.id = id
        self.email = email
        self.nombre = nombre
        self.id_rol = id_rol
        self.nombre_rol = nombre_rol
    
    @staticmethod
    def get(user_id):
        query = """
        SELECT u.id_usuario, u.correo, u.nombre_usuario, r.id_rol, r.nombre_rol 
        FROM Usuario u 
        JOIN RolUsuario ru ON u.id_usuario = ru.id_usuario 
        JOIN Rol r ON ru.id_rol = r.id_rol 
        WHERE u.id_usuario = ?
        """
        result = db.execute_query(query, (user_id,), fetch_one=True)
        
        if result:
            return User(
                id=result['id_usuario'],
                email=result['correo'],
                nombre=result['nombre_usuario'],
                id_rol=result['id_rol'],
                nombre_rol=result['nombre_rol']
            )
        return None
    
    @staticmethod
    def authenticate(email, password):
        query = """
        SELECT u.id_usuario, u.correo, u.nombre_usuario, u.contrasena_hash, r.nombre_rol
        FROM Usuario u 
        JOIN RolUsuario ru ON u.id_usuario = ru.id_usuario 
        JOIN Rol r ON ru.id_rol = r.id_rol 
        WHERE u.correo = ?
        """
        result = db.execute_query(query, (email,), fetch_one=True)
        
        if result:
            # Verificar contraseña (temporal - comparación directa)
            if result['contrasena_hash'] == password:  
                return User.get(result['id_usuario'])
        return None