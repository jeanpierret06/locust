import random
from locust import HttpUser, task, between

class CompueduLoadTest(HttpUser):
    # Tiempo de espera aleatorio entre 1 y 3 segundos entre tareas por cada usuario simulado
    wait_time = between(1, 3)

    @task(1)
    def cargar_home_page(self):
        """Requisito a): Simula la visita a la Home Page (Index)"""
        self.client.get("/")

    @task(2)
    def registrar_y_consultar_estudiante(self):
        """
        Requisitos b, c, d, e): 
        Simula la navegación desde el módulo principal, realiza un registro 
        y obtiene la consulta embebida de información.
        """
        # 1. Simular la llegada desde el módulo principal visitando el formulario (GET)
        self.client.get("/registro")
        
        # Generar datos aleatorios para evitar errores de llave duplicada (UniqueViolation)
        doc_rand = str(random.randint(100000, 99999999))
        payload = {
            "documento": doc_rand,
            "nombre": "Estudiante Carga Locust",
            "correo": f"locust_{doc_rand}@compuedu.edu.co",
            "programa": "ADSO",
            "ficha": "2670687"
        }
        
        # 2. Enviar el formulario de registro (POST)
        # Se envía como 'data' (form-encoded) porque Flask lee request.form
        with self.client.post("/registro", data=payload, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 302:
                # Si tu app redirecciona tras el registro, se considera correcto
                response.success()
            else:
                response.failure(f"Fallo en el registro. Código de estado: {response.status_code}")