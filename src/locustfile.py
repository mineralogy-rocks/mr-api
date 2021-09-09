from locust import HttpUser, TaskSet, task
 
class UserBehavior(TaskSet):
 
    @task(1)    
    def list_post(self):
        headers = {'content-type': 'application/json', 'Accept-Encoding': 'gzip'}
        self.client.get(
            "/api/", 
            headers=headers, 
            name = "List all minerals"
            )
 
 
class WebsiteUser(HttpUser):
    tasks = [UserBehavior]