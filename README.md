# Finance Tracker


## Overview

The Finance Tracker is a web application written in Python designed to provide fundamental investors with essential tools for analyzing and evaluating stocks. This project utilizes Flask for the backend, Jinja2 for templating, and Bootstrap for frontend design. The application fetches financial data from external APIs and provides various financial metrics and calculations to assist in investment decisions.

## Features

- **Stock Watchlist**: Add and manage a personalized list of stocks to track.
- **Stock Information**: Fetch and display detailed financial data for individual stocks.
- **Intrinsic Value Calculation**: Calculate intrinsic values based on revenue growth, margins, and other financial metrics.
- **Portfolio Management**: Manage and analyze your stock portfolio.
- **Email Notifications**: Get notified when stock prices reach your specified targets.
- **Auto-Fill**: Automatically fill input fields with pre-defined values for easier calculations.

## Technologies Used

- **Backend**: Flask
- **Frontend**: Jinja2, Bootstrap
- **Database**: SQLite
- **APIs**: Financial data fetched from Financial Modeling Prep

## Setup and Installation


### Installation

1. **Clone the repository**:
    

2. **Create and activate a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up the environment variables**:
    Create a `.env` file in the project root directory and add your API key:
    ```env
    FMP_API_KEY=your_api_key_here (from Financial Modeling Prep)
    ```

5. **Initialize the database**:
    ```bash
    flask db init
    flask db migrate
    flask db upgrade
    ```

6. **Run the application**:
    ```bash
    flask run
    ```

### Usage

- **Home Page**: View and manage your watchlist.
- **Stock Page**: View detailed information for a selected stock.
- **Calculations Page**: Perform intrinsic value calculations and set your own price target.
- **Portfolio Page**: Manage your portfolio holdings

