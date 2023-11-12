import datetime
import random
import time
import configparser
from csv import DictReader
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import mysql.connector
from mysql.connector import Error
import os

num_replace = {"K": 1000, "M": 1000000, "B": 1000000000}

button_getting_started = '//*[@id="channel-points-reward-center-body"]/div/div/div[2]/button'

button_my_channel_points = "//button[@aria-label='Points Balance']"
text_my_channel_points = "//span[@class='ScAnimatedNumber-sc-1iib0w9-0']"

button_prediction_prompt = "//div[@class='Layout-sc-1xcs6mc-0 dnxIGn predictions-list-item__body']"

button_if_voted = "//button[@data-test-selector='prediction-checkout-completion-step__details-button']//div[@class='Layout-sc-1xcs6mc-0 bFxzAY'][normalize-space()='See Details']"

text_submission = "//p[@class='CoreText-sc-1txzju1-0 hBNmlp']"

text_prediction = '//*[@id="channel-points-reward-center-body"]/div/div/div/div/div/div/div[1]/p[1]'
text_game = "//span[@class='CoreText-sc-1txzju1-0 dLeJdh']"

button_predict_with_custom_amount = "//*[@id='channel-points-reward-center-body']/div/div/div/div/div/div/div[3]/div[2]/button/div/div"

input_vote_blue = "//div[@class='Layout-sc-1xcs6mc-0 hVZAXf']//input[@type='number']"
input_vote_red = "//div[@class='Layout-sc-1xcs6mc-0 jOVwMQ']//input[@type='number']"

#button_vote_blue = "//div[@class='Layout-sc-1xcs6mc-0 hVZAXf']//div[@class='InjectLayout-sc-1i43xsx-0 custom-prediction-button__interactive jpJwfP']"
#button_vote_red = "//div[@class='Layout-sc-1xcs6mc-0 jOVwMQ']//div[@class='InjectLayout-sc-1i43xsx-0 custom-prediction-button__interactive jpJwfP']"

text_blue_votes_total = '//*[@id="channel-points-reward-center-body"]/div/div/div/div/div/div/div[2]/div/div[1]/div/div/div[3]/div[1]/div[1]/div/div/div[2]/p/span'
text_red_votes_total = '//*[@id="channel-points-reward-center-body"]/div/div/div/div/div/div/div[2]/div/div[2]/div/div/div[3]/div[1]/div[1]/div/div/div[2]/p/span'

text_blue_votes_win = "//div[@class='Layout-sc-1xcs6mc-0 gwcJMc']"
text_red_votes_win = "//div[@class='Layout-sc-1xcs6mc-0 gXiKJb']"

time_live = "//div[@class='Layout-sc-1xcs6mc-0 bKPhAm']"

three_plus_votes = "//div[@class='Layout-sc-1xcs6mc-0 kILIqT chat-input']//div[@class='simplebar-scroll-content']//div[3]//button[1]"

blue_points_spent = "//div[@class='Layout-sc-1xcs6mc-0 dyVPml']//p[@class='CoreText-sc-1txzju1-0']"
red_points_spent = "//div[@class='Layout-sc-1xcs6mc-0 kOwoNe']//p[@class='CoreText-sc-1txzju1-0']"
close_button = "//button[@aria-label='Close']"

button_see_details = "//button[@data-test-selector='prediction-checkout-completion-step__details-button']"
button_claim_bonus = "//button[@aria-label='Claim Bonus']"

chrome_options = webdriver.ChromeOptions()
# Füge hier weitere Chrome-Optionen hinzu, falls nötig

# Verwende den Service mit dem relativen Pfad zum Chromedriver
ser = Service(r".\webdriver\chromedriver.exe")

# Initialisiere den ChromeWebDriver mit dem Service-Objekt und den Chrome-Optionen
driver = webdriver.Chrome(service=ser, options=chrome_options)

# Initialisiere den WebDriverWait
wait = WebDriverWait(driver, 5)



def read_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config

def start_stream():
    CHANNEL_NAME = get_channel_name()
    #STREAMER = f"https://www.twitch.tv/popout/{CHANNEL_NAME}/chat"
    STREAMER = f"https://www.twitch.tv/{CHANNEL_NAME}"
    driver.get(STREAMER)
    upload_cookies()

def get_cookie_values(file):
    with open(file, encoding="utf-8-sig") as f:
        dict_reader = DictReader(f)
        list_of_dicts = list(dict_reader)
    return list_of_dicts

def upload_cookies():
    cookies = get_cookie_values("twitch_cookies.csv")
    for i in cookies:
        driver.add_cookie(i)

    driver.refresh()

def init():
    click_button(button_my_channel_points)
    click_button(button_getting_started)
    click_button(button_my_channel_points)

def channel_bets_total(color_win):

    config = read_config()
    host = config.get('Database', 'host')
    port = config.getint('Database', 'port')
    database = config.get('Database', 'database')
    user = config.get('Database', 'user')
    password = config.get('Database', 'password')
    CHANNEL_NAME = get_channel_name()

    time_now = datetime.datetime.now().strftime('%H:%M:%S')
    formatted_date = datetime.datetime.now().strftime('%d-%b-%y')
    file_name = f"{CHANNEL_NAME}_channel_preditcion_total.txt"

    str_my_channel_points = text_XPATH(text_my_channel_points)
    str_total_blue_points = text_XPATH(text_blue_votes_total)
    str_total_red_points = text_XPATH(text_red_votes_total)

    my_points = num_string_to_int(str_my_channel_points)
    points_blue = num_string_to_int(str_total_blue_points)
    points_red = num_string_to_int(str_total_red_points)
    current_game = text_XPATH(text_game)
    submission_text = text_XPATH(text_prediction)

    try:
        # MySQL connection configuration
        connection = mysql.connector.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Check if the table exists, if not, create it
            create_table_query = f"""
                CREATE TABLE IF NOT EXISTS {CHANNEL_NAME} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date VARCHAR(20),
                    time VARCHAR(20),
                    curpoints INT,
                    blupoints INT,
                    redpoints INT,
                    curgame VARCHAR(50),
                    bet_text VARCHAR(255),
                    winner INT
                )
            """
            cursor.execute(create_table_query)

            # Insert data into the table
            insert_query = f"""
                INSERT INTO {CHANNEL_NAME}
                    (date, time, curpoints, blupoints, redpoints, curgame, bet_text, winner)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            data = (formatted_date, time_now, my_points, points_blue, points_red, current_game, submission_text, color_win)
            cursor.execute(insert_query, data)

            connection.commit()
            print("Record inserted successfully into MySQL table")

    except Error as e:
        print(f"Error: {e}")

    finally:
        # Close the database connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

    try:
        with open(file_name, "r") as file:
            first_line = file.readline()
    except FileNotFoundError:
        first_line = ""

    with open(file_name, "a") as file:
        if "date" in first_line:
            file.write(
                f"{formatted_date},{time_now},{my_points},{points_blue},{points_red},{current_game},{submission_text},{color_win}\n"
            )
        else:
            file.write(
                f"date,time,curpoints,blupoints,redpoints,curgame,bet_text,winner\n"
                f"{formatted_date},{time_now},{my_points},{points_blue},{points_red},{current_game},{submission_text},{color_win}\n"
            )
    
def text_XPATH(XPATH_var):
    return driver.find_element(By.XPATH, XPATH_var).text

def click_button(variable):
    var = wait.until(EC.element_to_be_clickable((By.XPATH, variable)))
    var.click()  

def autoclicker():
    clicker_points = wait.until(EC.element_to_be_clickable((By.XPATH, button_claim_bonus)))
    actions = ActionChains(driver)
    actions.click_and_hold(clicker_points).perform()  
    time.sleep(1)  
    actions.release(clicker_points).perform()

def pure_number(number, string):
    mult = 1.0
    if string in num_replace:
        x = num_replace[string]
        mult *= x
        return int(number * mult)

def num_string_to_int(current_points):
        if "K" in current_points:
            num = float(current_points.split("K")[0])
            character = current_points[len(current_points) - 1:]
            current_points = pure_number(number=num, string=character)
            return current_points
        
        elif "M" in current_points:
            num = float(current_points.split("M")[0])
            character = current_points[len(current_points) - 1:]
            current_points = pure_number(number=num, string=character)
            return current_points
        elif "B" in current_points:
            num = float(current_points.split("M")[0])
            character = current_points[len(current_points) - 1:]
            current_points = pure_number(number=num, string=character)
            return current_points
        else:
            num = float(current_points)
            return int(current_points)

def get_points(current_points):
    if current_points < 1540:
        points_to_bet = 100
        return points_to_bet
    
    elif current_points > 250000:
        points_to_bet = 250000
        return points_to_bet
    
    else:
        points_to_bet = (round(current_points * 0.065))
        return points_to_bet

def time_set(total_time):

    time_remaining = total_time.split(":")
    print("minutes: ", time_remaining[0])
    print("seconds: ", time_remaining[1])
    minutes = int(time_remaining[0])
    seconds = int(time_remaining[1])
    
    if minutes == 0:
        return
    elif minutes == 1:
        time.sleep(seconds)
        print("Waiting seconds", seconds)
        return
    else:
        print("Waiting 20 seconds")
        time.sleep(20)
        #time.sleep(((minutes - 1) * 60) + seconds)
        return
    
def hold(timer=2,random_range=0):
    time.sleep(timer + (random.randint(0,random_range)))

def get_winner():
    return wait.until(EC.text_to_be_present_in_element((By.XPATH, text_blue_votes_win),"Winner"))

def get_channel_name():
    config_path = os.path.join(os.path.dirname(__file__), 'config.ini')

    folder_path, file_name = os.path.split(config_path)

    folder_name = os.path.basename(folder_path)
    return folder_name

CHANNEL_NAME = get_channel_name()