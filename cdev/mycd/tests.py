from django.test import TestCase

class SimpleTest(TestCase):
			
	def test_register_logout_login(self):
		self.client.post('/register/', {"username": "test_user", "password1": "test_pw", "password2": "test_pw"})
		self.client.get('/logout/')
		response = self.client.post('/login/', {"username": "test_user", "password": "test_pw"})
		self.assertEqual(response.status_code, 302) #redirect on form success
	
	def test_views(self):
		views = ['/', '/register/', '/login/', '/export/', '/import/']
		for view in views:
			print 'No login: testing view: ' + view
			response = self.client.get(view)
			self.assertEqual(response.status_code, 200)

		views = ['/dashboard/', '/logout/', '/contacts/']
		for view in views:
			print 'No login: testing view: ' + view
			response = self.client.get(view)
			self.assertEqual(response.status_code, 302) #moved for failed permissions

		self.client.post('/register/', {"username": "test_user", "password1": "test_pw", "password2": "test_pw"})
		
		views = ['/', '/dashboard/', '/export/', '/import/', '/contacts/']
		for view in views:
			print 'Logged in: testing view: ' + view
			response = self.client.get(view)
			self.assertEqual(response.status_code, 200)
			
		views = ['/register/', '/login/']
		for view in views:
			print 'Logged in: testing view: ' + view
			response = self.client.get(view)
			self.assertEqual(response.status_code, 302) #redirect when logged in
			
__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

