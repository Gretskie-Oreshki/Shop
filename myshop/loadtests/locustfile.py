from locust import HttpUser, task, between
import random

class ShopUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # если нужен логин — делаем его один раз
        response = self.client.post("/login/", {
            "username": "testuser",
            "password": "testpass"
        })

    @task(3)
    def view_products(self):
        self.client.get("/products/")

    @task(5)
    def view_product_detail(self):
        product_id = random.randint(1, 50)
        self.client.get(f"/products/{product_id}/")

    @task(2)
    def add_to_cart(self):
        product_id = random.randint(1, 50)
        self.client.post("/cart/add/", {
            "product_id": product_id,
            "quantity": 1
        })

    @task(1)
    def home(self):
        self.client.get("/")