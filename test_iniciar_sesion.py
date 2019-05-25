import json
import unittest
import requests 
import hashlib

class iniciar_sesion_test(unittest.TestCase):
    
    def registrar_usuario(self, user_name, user_email, user_password):
        service_end_point = 'http://localhost:5000/registrar_usuario'
        data = dict(user_name = user_name, user_email = user_email, user_password = user_password)
        headers = {'Content-type': 'application/json'}
        response = requests.post(url = service_end_point, data = json.dumps(data), headers = headers)
        return response

    def iniciar_sesion(self, user_email, user_password):
        service_end_point = 'http://localhost:5000/iniciar_sesion'
        user_password_sha256 = hashlib.sha256(user_password.encode()).hexdigest()
        data = dict(user_email = user_email, user_password = user_password_sha256)
        headers = {'Content-type': 'application/json'}
        response = requests.post(url = service_end_point, data = json.dumps(data), headers = headers)
        return response
    
    # Iniciar sesión con un usuario que no existe 
    def test_1(self):
        user_name = 'no_existe@correo.com'
        user_password = '12345'
        response = self.iniciar_sesion(user_name, user_password)
        message = json.loads(response.text).get('message')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(message, 'Usuario/contraseña incorrectos') 

    # Iniciar sesión con un usuario existente pero con contraseña incorrcta
    def test_2(self):
        user_name = 'john doe'
        user_email = 'j.doe@email.com'
        user_password = 'ABCD'
        # Registrar usuario 
        self.registrar_usuario(user_name, user_email, user_password)
        user_password_error = '12345'
        response = self.iniciar_sesion(user_email, user_password_error)
        message = json.loads(response.text).get('message')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(message, 'Usuario/contraseña incorrectos') 

    # Iniciar sesion con un usuario existente con contraseña correcta (usa el set_up del test_2)
    def test_3(self):
        user_email = 'j.doe@email.com'
        user_password = 'ABCD'
        response = self.iniciar_sesion(user_email, user_password)
        message = json.loads(response.text).get('message')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(message, 'Sesión iniciada')
    
if __name__ == "__main__":
    unittest.main()