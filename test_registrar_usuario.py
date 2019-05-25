import json
import unittest
import requests 

class registrar_usuario_test(unittest.TestCase):
    
    def registrar_usuario(self, user_name, user_email, user_password):
        service_end_point = 'http://localhost:5000/registrar_usuario'
        data = dict(user_name = user_name, user_email = user_email, user_password = user_password)
        headers = {'Content-type': 'application/json'}
        response = requests.post(url = service_end_point, data = json.dumps(data), headers = headers)
        return response
    
    # Intenta registrar un nuevo usuario que no esta en la base de datos
    def test_1(self):
        response = self.registrar_usuario('afg', 'af.guzman@outlook.com', '1234')
        message = json.loads(response.text).get('message')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(message, 'Usuario af.guzman@outlook.com registrado de forma exitosa')

    # Intenta registrar un usuario que ya existe en la base de datos
    def test_2(self):
        response = self.registrar_usuario('afg', 'af.guzman@outlook.com', '1234')
        message = json.loads(response.text).get('message')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(message, 'Usuario af.guzman@outlook.com ya existe en el sistema')
    
    # Intenta registrar un usuario con algun campo en blanco
    def test_3(self):
        response = self.registrar_usuario('afg', '  ', '1234')
        message = json.loads(response.text).get('message')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(message, 'Hay campos en blanco') 
    
if __name__ == "__main__":
    unittest.main()