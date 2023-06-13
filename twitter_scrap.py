import csv
import mysql.connector
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Connect to MySQL
cnx = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='Danurag23@',
    database='anurag'
)
cursor = cnx.cursor()
table_name = 'twitter_profiles'

# Create the table if it doesn't exist
create_table_query = '''
CREATE TABLE IF NOT EXISTS {} (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bio TEXT,
    following_count INT(11) DEFAULT 0,
    followers_count INT(11) DEFAULT 0,
    location VARCHAR(255) DEFAULT '',
    website VARCHAR(255) DEFAULT ''
)
'''.format(table_name)

cursor.execute(create_table_query)

# Function to write data to MySQL
def write_to_mysql(data):
    insert_query = '''
    INSERT INTO {} (bio, following_count, followers_count, location, website)
    VALUES (%s, %s, %s, %s, %s)
    '''.format(table_name)

    values = (
        data['Bio'],
        data['Following Count'],
        data['Followers Count'],
        data['Location'],
        data['Website']
    )

    try:
        cursor.execute(insert_query, values)
        cnx.commit()
        print("Data inserted into MySQL successfully")
    except mysql.connector.Error as error:
        print(f"Error inserting data into MySQL: {error}")

# Function to scrape a Twitter profile
def scrape_twitter_profile(url):
    options = Options()
    options.add_argument("--headless")

    # Set path to your ChromeDriver executable
    chromedriver_path = r'C:\Users\hello\AppData\Local\Programs\Python\Python311\Scripts\chromedriver.exe'

    service = Service(chromedriver_path)

    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)

        # Wait for the bio element to be visible
        wait = WebDriverWait(driver, 10)
        bio_element = wait.until(EC.visibility_of_element_located((By.XPATH, '//div[@data-testid="UserDescription"]')))
        bio = bio_element.text
    except TimeoutException:
        bio = ''

    # Find the following count element using XPath
    try:
        following_element = driver.find_element(By.XPATH, '//div[@class="css-1dbjc4n r-1mf7evn"]//span[@class="css-901oao css-16my406 r-poiln3 r-bcqeeo r-qvutc0"]')
        following_count = following_element.text
    except NoSuchElementException:
        following_count = '0'

    # Find the followers count element using XPath
    try:
        followers_count_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//a[contains(@href, "/followers")]//span[@class="css-901oao css-16my406 r-poiln3 r-bcqeeo r-qvutc0"]'))
        )
        followers_count = followers_count_element.get_attribute('textContent')
    except TimeoutException:
        followers_count = '0'
    except NoSuchElementException:
        followers_count = '0'

    # Find the location element using XPath
    try:
        location_element = driver.find_element(By.XPATH, '//span[@data-testid="UserLocation"]//span')
        location = location_element.text
    except NoSuchElementException:
        location = ''

    # Find the website element using XPath
    try:
        website_element = driver.find_element(By.XPATH, '//a[@data-testid="UserUrl"]')
        website = website_element.get_attribute("href")
    except NoSuchElementException:
        website = ''

    # Close the browser
    driver.quit()

    # Create a dictionary with the scraped data
    data = {
        'Bio': bio,
        'Following Count': following_count,
        'Followers Count': followers_count,
        'Location': location,
        'Website': website
    }

    return data

file_name = 'twitter_links.csv'

# Read URLs from CSV file and scrape profiles
with open(file_name, 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        url = row[0]
        data = scrape_twitter_profile(url)
        write_to_mysql(data)
        print(data)

# Close the MySQL connection
cnx.close()
