# -*- coding: utf-8 -*-
import logging
import re
import time
import math
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import init, Fore, Style
import os

init(autoreset=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


driver = webdriver.Chrome()


def login_first(driver):
    driver.get("https://ops.miswag.co")
    time.sleep(2)
    print(Fore.GREEN + "Login and press enter .." + Style.RESET_ALL, end='')
    input("")


def check_dispatch(driver):
    print(Fore.GREEN + "Update urls.txt file to add your dispatch orders, if done press enter..." + Style.RESET_ALL, end='')
    input()
    with open('urls.txt', 'r') as file:
        content = file.read()
        urls = content.split(',')
    for url in urls:
        dispatch_url = url.strip()
        try:
            false_counter = 0
            driver.get(dispatch_url)
            dispatch_name_match = dispatch_url.split("dispatches/")[1]
            dispatch_date_from_xpath = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '/html/body/div[2]/div[2]/main/div/section/header[1]/div[1]/h1'))
            ).text.strip()
            dispatch_date = re.search(r"(\d{2}/\d{2}/\d{4})", dispatch_date_from_xpath).group(1)

            dispatch_by = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '/html/body/div[2]/div[2]/main/div/section/header[2]/div/div/div[3]/span'))
            ).text.strip()
            dispatch_agent = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '/html/body/div[2]/div[2]/main/div/section/header[2]/div/div/div[2]/span'))
            ).text.strip()
            logging.info(f"For dispatch {dispatch_date} \nTo agent: {dispatch_agent}\nCreated by: {dispatch_by}")
            per_page = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH,
                     '//*[@id="relationManager0"]/div/div/div/nav/div/label[2]/div/div[2]/select/option[4]'))
            )
            per_page.click()
            logging.info("Set items per page to 100")
            showed_count = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="relationManager0"]/div/div/div/nav/span'))
            )
            showed_count_text = showed_count.text.strip()
            match = re.search(r"of (\d+) results", showed_count_text)
            number = int(match.group(1)) if match else 0
            logging.info(f"Extracted number of results: {number}")
            perfect_orders = []
            imperfect_orders = []
            total_pages = math.ceil(number / 100)
            logging.info(f"Pages: {total_pages}")
            if total_pages > 1:
                for page_num in range(1, total_pages + 1):
                    driver.get(f"{dispatch_url}?page={page_num}")
                    per_page = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH,
                             '//*[@id="relationManager0"]/div/div/div/nav/div/label[2]/div/div[2]/select/option[4]'))
                    )
                    per_page.click()
                    logging.info("Set items per page to 100")

                    showed_count = WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located(
                            (By.XPATH, '//*[@id="relationManager0"]/div/div/div/nav/span'))
                    )
                    showed_count_text = showed_count.text.strip()
                    match2 = re.search(r"Showing (\d+) to (\d+) of (\d+) results", showed_count_text)
                    loopy = (int(match2.group(2)) - int(match2.group(1))) + 1
                    logging.info(f"In page: {dispatch_url}?page={page_num} with orders: {number}")
                    for i in range(2, loopy + 2):
                        order_text = "unknown"
                        try:
                            xp = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH,
                                                            f'//*[@id="relationManager0"]/div/div/div/div[2]/table/tbody/tr[{i}]/td[1]/div/div/div/div/div/div/span'))
                            )
                            xp2 = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH,
                                                            f'//*[@id="relationManager0"]/div/div/div/div[2]/table/tbody/tr[{i}]/td[10]/div/div/a/span'))
                            )
                            order_text = xp.text.strip()
                            if not order_text:
                                logging.warning(f"Skipping order {i} as it is empty or None")
                                continue
                            xp2.click()
                            logging.info(f"Clicked on order {i}: {order_text}")
                            driver.switch_to.window(driver.window_handles[1])
                            time.sleep(1)
                            dateoforder_xpath = WebDriverWait(driver, 10).until(
                                EC.visibility_of_element_located(
                                    (By.XPATH,
                                     '/html/body/div[2]/div[2]/main/div/section/header/div[1]/div[2]/div[2]'))
                            ).text.strip()
                            order_date = re.search(r"(\d{2})-(\d{2})-(\d{4})", dateoforder_xpath).group(
                                0).replace("-", "/")
                            if order_date:
                                status = order_date == dispatch_date
                                logging.info(
                                    f"Order received on {order_date} and dispatch date {dispatch_date}, status: {status}")
                                if status:
                                    perfect_orders.append(order_text)
                                    false_counter = 0
                                else:
                                    imperfect_orders.append(order_text)
                                    false_counter += 1
                                    logging.warning(
                                        f"Order date mismatch for order {order_text}. False counter: {false_counter}")

                                    if false_counter >= 3:
                                        logging.error("Too many mismatches, moving to the next URL.")
                                        driver.close()
                                        driver.switch_to.window(driver.window_handles[0])
                                        break
                                driver.close()
                                driver.switch_to.window(driver.window_handles[0])
                            else:
                                logging.warning(f"No valid order date found.")
                                order_date = None
                        except Exception as e:
                            logging.error(f"Error processing order {i}: {order_text}. Error: {e}")
                            imperfect_orders.append(order_text)
            elif total_pages == 1:
                logging.info("One page")
                for i in range(2, number + 3):
                    order_text = "unknown"
                    try:
                        xp = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH,
                                                        f'//*[@id="relationManager0"]/div/div/div/div[2]/table/tbody/tr[{i}]/td[1]/div/div/div/div/div/div/span'))
                        )
                        xp2 = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH,
                                                        f'//*[@id="relationManager0"]/div/div/div/div[2]/table/tbody/tr[{i}]/td[10]/div/div/a/span'))
                        )
                        order_text = xp.text.strip()
                        if not order_text:
                            logging.warning(f"Skipping order {i} as it is empty or None")
                            continue
                        xp2.click()
                        logging.info(f"Clicked on order {i}: {order_text}")
                        driver.switch_to.window(driver.window_handles[1])
                        time.sleep(1)
                        comments_loaded = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH,
                                                            '/html/body/div[2]/div[2]/main/div/section/div/div/div[3]/div[1]/div[2]/div/div/div/div[1]/div[1]/div[2]'))
                        )
                        dateoforder_xpath = WebDriverWait(driver, 10).until(
                            EC.visibility_of_element_located(
                                (By.XPATH, '/html/body/div[2]/div[2]/main/div/section/header/div[1]/div[2]/div[2]'))
                        ).text.strip()
                        order_date = re.search(r"(\d{2})-(\d{2})-(\d{4})", dateoforder_xpath).group(
                            0).replace("-", "/")
                        if order_date:
                            status = order_date == dispatch_date
                            logging.info(
                                f"Order received on {order_date} and dispatch date {dispatch_date}, status: {status}")
                            if status:
                                perfect_orders.append(order_text)
                                false_counter = 0
                            else:
                                imperfect_orders.append(order_text)
                                false_counter += 1
                                logging.warning(
                                    f"Order date mismatch for order {order_text}. False counter: {false_counter}")
                                if false_counter >= 3:
                                    logging.error("Too many mismatches, moving to the next URL.")
                                    driver.close()
                                    driver.switch_to.window(driver.window_handles[0])
                                    break
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                        else:
                            logging.warning(f"No valid order date found.")
                            order_date = None
                    except Exception as e:
                        logging.error(f"Error processing order {i}: {order_text}. Error: {e}")
                        imperfect_orders.append(order_text)
            else:
                logging.info("Nothing to process")
            dispatch_folder_name = dispatch_date.replace("/", "-")
            if not os.path.exists(dispatch_folder_name):
                os.makedirs(dispatch_folder_name)
                logging.info(f"Created directory: {dispatch_folder_name}")
            file_path = os.path.join(dispatch_folder_name, f"Dispatch #{dispatch_name_match}.txt")
            with open(file_path, "w", encoding="utf-8") as result_file:
                result_file.write(f"Dispatch Date: {dispatch_date}\n")
                result_file.write(f"Created by: {dispatch_by}\n")
                result_file.write(f"To agent: {dispatch_agent}\n")
                result_file.write(f"\nPerfect Orders ({len(perfect_orders)}):\n")
                result_file.write("\n".join(perfect_orders))
                result_file.write(f"\n\nImperfect Orders ({len(imperfect_orders)}):\n")
                result_file.write("\n".join(imperfect_orders))
            logging.info(f"Results saved to {file_path}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")


login_first(driver)

def main():
    check_dispatch(driver)
    print(Fore.GREEN + "Do you want to perform a new check? (yes/no): " + Style.RESET_ALL, end='')
    if input().strip().lower() != 'yes':
        print(Fore.GREEN + "Closing the application..." + Style.RESET_ALL, end='')
        driver.quit()


if __name__ == "__main__":
    main()

