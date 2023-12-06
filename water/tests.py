from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from .models import Building, WaterStation
from django.urls import reverse

from .views import is_admin, is_base, is_logged_in


class BuildingModelTest(TestCase):
    def setUp(self):
        self.building = Building.objects.create(
            name="Test Building",
            lat=42.12345,
            lng=12.54321,
            place_id="test_place_id"
        )

    def test_building_creation(self):
        self.assertEqual(self.building.name, "Test Building")
        self.assertEqual(self.building.lat, 42.12345)
        self.assertEqual(self.building.lng, 12.54321)
        self.assertEqual(self.building.place_id, "test_place_id")

class WaterStationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.building = Building.objects.create(
            name="Test Building",
            lat=42.12345,
            lng=12.54321,
            place_id="test_place_id"
        )
        self.water_station = WaterStation.objects.create(
            user=self.user,
            building=self.building,
            floor=1,
            cardinal="n",
            traditional=True,
            bottle=False,
            approved=False
        )

    def test_water_station_creation(self):
        self.assertEqual(self.water_station.user, self.user)
        self.assertEqual(self.water_station.building, self.building)
        self.assertEqual(self.water_station.floor, 1)
        self.assertEqual(self.water_station.cardinal, "n")
        self.assertTrue(self.water_station.traditional)
        self.assertFalse(self.water_station.bottle)
        self.assertFalse(self.water_station.approved)

class WaterStationTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpass', email='test@example.com')

        # Create admin and base groups
        self.admin_group = Group.objects.create(name='admin')
        self.base_group = Group.objects.create(name='base')

        # Assign the user to the base group
        self.user.groups.add(self.base_group)

        # Create a test building
        self.building = Building.objects.create(name='Test Building', lat=0.0, lng=0.0, place_id='test_place_id')

        # Create a test water station
        self.water_station = WaterStation.objects.create(
            user=self.user,
            building=self.building,
            floor=1,
            cardinal='c',
            traditional=True,
            bottle=False,
            approved=True
        )

        # Create a client for making requests
        self.client = Client()

    def test_home_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_map_view(self):
        response = self.client.get(reverse('map'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'map.html')

    def test_map_stations_view(self):
        response = self.client.get(reverse('map_stations', args=[self.building.place_id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'map_stations.html')

    def test_submit_water_station_view(self):
        self.client.login(username='testuser', password='testpass')

        response = self.client.get(reverse('submit_water_station'))
        self.assertEqual(response.status_code, 200)

    def test_submit_water_station_view_not_authenticated(self):
        # user is not logged in
        response = self.client.get(reverse('submit_water_station'))

        # Assert that the response status code is a redirect (302) to the login URL
        self.assertEqual(response.status_code, 302)
        # self.assertContains(response, "You don't have access to this page")

    def test_approve_water_station_view(self):
        # Login an admin user
        self.user.groups.add(self.admin_group)
        self.client.login(username='testuser', password='testpass')

        response = self.client.get(reverse('approve_water_station'))
        self.assertEqual(response.status_code, 200)

    def test_approve_water_station_view_not_authenticated(self):
        # user is not logged in
        response = self.client.get(reverse('approve_water_station'))

        # Assert that the response status code is a redirect (302) to the login URL
        self.assertEqual(response.status_code, 302)
        # self.assertContains(response, "You don't have access to this page")

    def test_approve_water_station_view_not_admin(self):
        # user is logged in, but not as admin
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('approve_water_station'))

        # Assert that the response status code is a redirect (302) to the login URL
        self.assertEqual(response.status_code, 302)
        # self.assertContains(response, "You don't have access to this page")

    def test_user_water_stations_view(self):
        # Login the user first
        self.client.login(username='testuser', password='testpass')

        response = self.client.get(reverse('user_water_stations'))
        self.assertEqual(response.status_code, 200)

    def test_user_water_stations_view_not_authenticated(self):
        # user not logged in
        response = self.client.get(reverse('user_water_stations'))
        # Assert that the response status code is a redirect (302) to the login URL
        self.assertEqual(response.status_code, 302)
        # self.assertContains(response, "You don't have access to this page")

    def test_user_water_stations_view_not_base(self):
        # Login the user first
        self.user.groups.add(self.admin_group)
        self.client.login(username='testuser', password='testpass')

        response = self.client.get(reverse('user_water_stations'))
        # Assert that the response status code is a redirect (302) to the login URL
        self.assertEqual(response.status_code, 302)
        # self.assertContains(response, "You don't have access to this page")

    def test_logout_view(self):
        # Log in as a user
        self.client.login(username="testuser", password="testpassword")

        # Test logging out
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Expect a redirect to the home page

    def test_submit_water_station_form_valid_submission(self):
        # Login the user first
        self.client.login(username='testuser', password='testpass')

        response = self.client.post(reverse('submit_water_station'), {
            'building': self.building.id,
            'floor': 1,
            'cardinal': 'c',
            'traditional': True,
            'bottle': False,
        })

        self.assertRedirects(response, reverse('submit_water_station'))

        # Check if the water station is created
        new_station = WaterStation.objects.latest('id')
        self.assertEqual(new_station.user, self.user)
        self.assertEqual(new_station.building, self.building)
        self.assertEqual(new_station.floor, 1)
        self.assertEqual(new_station.cardinal, 'c')
        self.assertTrue(new_station.traditional)
        self.assertFalse(new_station.bottle)
        self.assertFalse(new_station.approved)

    def test_approve_water_station_approves_station(self):
        # Login an admin user
        self.user.groups.add(self.admin_group)
        self.client.login(username='testuser', password='testpass')

        # Create an unapproved water station
        unapproved_station = WaterStation.objects.create(
            user=self.user,
            building=self.building,
            floor=1,
            cardinal='c',
            traditional=True,
            bottle=False,
            approved=False
        )

        # Make a GET request to the approve_water_station view
        response = self.client.get(reverse('approve_water_station'))

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Assert that the unapproved station is present in the response content
        # print(response.content)
        self.assertContains(response, f'Submitted by: {self.user.email}')

        # Make a POST request to approve the water station
        response = self.client.post(reverse('approve_water_station'),
                                    data={f'radio-group-{unapproved_station.id}': 'approved'})

        # Assert that the response status code is a redirect (302)
        self.assertEqual(response.status_code, 302)

        # Assert that the water station is now approved in the database
        unapproved_station.refresh_from_db()
        self.assertTrue(unapproved_station.approved)

    def test_map_stations_view_displays_stations(self):
        response = self.client.get(reverse('map_stations', args=['test_place_id']))
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, 'Map Stations')

        # Ensure that approved water stations are displayed
        self.assertContains(response, self.water_station.building.name)

        # Create another approved water station
        station2 = WaterStation.objects.create(
            user=self.user,
            building=self.building,
            floor=2,
            cardinal='n',
            traditional=False,
            bottle=True,
            approved=True
        )

        response = self.client.get(reverse('map_stations', args=['test_place_id']))
        self.assertContains(response, station2.building.name)
        self.assertContains(response, self.water_station.building.name)

    def test_is_admin_function(self):
        # Create an admin user
        self.user.groups.add(self.admin_group)

        self.assertTrue(is_admin(self.user))

    def test_is_base_function(self):
        self.assertTrue(is_base(self.user))

    def test_is_logged_in_function(self):
        self.client.login(username='testuser', password='testpass')
        self.assertTrue(is_logged_in(self.user))
