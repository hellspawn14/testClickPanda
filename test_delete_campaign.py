import json
import unittest
import requests 
import hashlib
import time

class create_delete_campaign_test(unittest.TestCase):
    
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

    def delete_campaign(self, id_campaign):
        service_end_point = 'http://localhost:5000/delete_campaign'
        data = dict(id_campaign = id_campaign)
        headers = {'Content-type': 'application/json'}
        response = requests.post(url = service_end_point, data = json.dumps(data), headers = headers)
        return response 
    
    # Eliminar una campania que no existe
    def test_1(self):
        id_campaign = '123445'
        response = self.delete_campaign(id_campaign)
        message = json.loads(response.text).get('message')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(message, 'La campania no existe') 

    # Eliminar una campania existente 
    def test_2(self):
        user_name = 'john doe'
        user_email = 'j.doe@email.com'
        user_password = 'ABCD' 
        # Registrar usuario para test
        self.registrar_usuario(user_name, user_email, user_password)
        subject = 'This is a test'
        number_of_recipients = 10
        # Crear campaña y obtener ID
        response = self.create_new_campaign(user_email, subject, number_of_recipients)
        id_campaign = json.loads(response.text).get('id_campaign')
        
        time.sleep(10) 

        response = self.delete_campaign(id_campaign)
        self.assertEqual(response.status_code, 200)
        message = json.loads(response.text).get('message')
        self.assertEqual(message, 'Status campania modificado') 
        status_campain = json.loads(response.text).get('change_status')
        self.assertEqual(status_campain, 0) 
    
if __name__ == "__main__":
    unittest.main()