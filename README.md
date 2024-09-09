# Dispatch Order Checker

## Overview

This script automates the process of checking dispatch orders on the [Miswag Operations Platform](https://ops.miswag.co). It uses Selenium WebDriver to navigate the site, interact with the dispatch orders, and collect relevant data. The collected data is saved into text files for further analysis.

## Features

- **Login Handling:** Prompts the user to manually log in before proceeding.
- **Dispatch URL Processing:** Reads dispatch URLs from `urls.txt`, processes each URL, and collects data.
- **Data Extraction:** Retrieves dispatch details and order information.
- **Pagination Handling:** Handles multiple pages of results by navigating through them.
- **Result Saving:** Saves results in a structured format within folders named by dispatch dates.

## Requirements

- **Python 3.x**
- **Selenium:** For web automation and interaction.
- **Colorama:** For colored terminal output.
- **Chromedriver:** Needed for Selenium to work with Google Chrome (except when using the executable version).

## Installation

**Clone the repository:**

   ```bash
   git clone https://github.com/dhurgham-miswag/same-day-dispatched-orders.git
   cd same-day-dispatched-orders
