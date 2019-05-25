import json
import unittest
import requests 
import hashlib

class create_new_campaign_test(unittest.TestCase):
    
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

    def create_new_campaign(self, user_email, subject, number_of_recipients):
        service_end_point = 'http://localhost:5000/create_new_campaign'
        data = dict(user_email = user_email, subject = subject, number_of_recipients = number_of_recipients)
        headers = {'Content-type': 'application/json'}
        response = requests.post(url = service_end_point, data = json.dumps(data), headers = headers)
        return response
    
    # Crear una campaña sin un usuario
    def test_1(self):
        user_email = 'non_existant@email.com'
        subject = 'This is a test'
        number_of_recipients = 10
        response = self.create_new_campaign(user_email, subject, number_of_recipients)
        message = json.loads(response.text).get('message')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(message, 'El usuario no existe') 

    # Crear una campaña con numero de receptores menor a 0 
    def test_2(self):
        user_name = 'john doe'
        user_email = 'j.doe@email.com'
        user_password = 'ABCD' 
        # Registrar usuario para test
        self.registrar_usuario(user_name, user_email, user_password)
        subject = 'This is a test'
        number_of_recipients = -10
        response = self.create_new_campaign(user_email, subject, number_of_recipients)
        message = json.loads(response.text).get('message')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(message, 'Una campaña debe tener al menos un receptor') 
    
    # Crear una campaña de forma exitosa (usa el set up de test_2)
    def test_3(self):
        user_email = 'j.doe@email.com'
        subject = 'This is a test'
        number_of_recipients = 10
        response = self.create_new_campaign(user_email, subject, number_of_recipients)
        message = json.loads(response.text).get('message')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(message, 'Campania creada')
    
if __name__ == "__main__":
    unittest.main()