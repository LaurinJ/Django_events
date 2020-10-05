import os

from django.test import LiveServerTestCase
from django.urls import reverse
from django.conf import settings

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

class AnonymousUserTest(LiveServerTestCase):

    fixture_files = ['users.json', 'events.json', 'eventruns.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fixtures =[os.path.join(settings.FIXTURE_DIRS[0],f) 
                        for f in cls.fixture_files]

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.wait = WebDriverWait(self.browser, 1)

    def tearDown(self):
        self.browser.close()

    def test_anonymous_user(self):
        # New visitor enters the url of detail_view into 
        # the browser 
        self.browser.get(self.live_server_url + reverse('cart:detail'))

        # She sees the detail page announcing there is nothing
        # in the shopping cart
        self.assertIn('Cart Detail', self.browser.title)

        # The visitor decides to go to the events page where
        # she selects the first event available
        events_link = self.browser.find_element_by_css_selector('#nav-buttons a:first-of-type')
        events_link.click()

        # Visitor is taken to the events page
        self.assertIn('Event Listing', self.browser.title)

        # Visitor select's the first event
        event = self.wait.until(lambda driver: driver.find_element(By.CLASS_NAME, 
                                                        'event-tile:first-of-type'))
        event.send_keys(Keys.RETURN)

        # The visitor does not have access to any delete nor update event nor eventrun links
        self.assertRaises(
            TimeoutException,
            lambda: self.wait.until(lambda driver: driver.find_element(By.CLASS_NAME, 'edit-button'))
        )
        endpoint = reverse('events:detail', args=[None]).rsplit('/', 2)[0]
        self.assertIn(endpoint, self.browser.current_url)

        # Looking at the detail element page, the visitor sees the possibility
        # of adding event run into a cart
        add_cart_button = self.browser.find_element(By.CSS_SELECTOR, 
                                    '.cart-add:first-child button')


        # The visitor accidentally clicks on the Add to Cart button keeping 
        # the number of items on 0
        add_cart_button.click()

        # The visitor is shown the event detail page with an error message
        # that the run could not be added into the cart 
        flash = self.wait.until(lambda driver: driver.find_element(By.CLASS_NAME, 'error'))
        self.assertIn('The run could not be added into the cart', flash.text)
        
        endpoint = reverse('events:detail', args=[None]).rsplit('/', 2)[0]
        self.assertIn(endpoint, self.browser.current_url)

        # The visitor now sets the number of runs to 1 and clicks on Add to Cart
        # button
        quantity_input = self.browser.find_element(By.CSS_SELECTOR, 
                                '.cart-add:first-child #id_quantity')
        quantity_input.clear()
        quantity_input.send_keys("1")
        add_cart_button = self.browser.find_element(By.CSS_SELECTOR, 
                                     '.cart-add:first-child button')
        add_cart_button.click()

        # The visitor gets the flash message that the event has been added to the cart
        # but stays on the same event detail page
        flash = self.wait.until(lambda driver: driver.find_element(By.CLASS_NAME, 'success'))
        self.assertIn('The run has been added to the cart', flash.text)

        endpoint = reverse('events:detail', args=[None]).rsplit('/', 2)[0]
        self.assertIn(endpoint, self.browser.current_url)

        self.fail('TEST END')
        # The visitor decides to put another event into the cart
       

        # The visitor now decides to check that cart
