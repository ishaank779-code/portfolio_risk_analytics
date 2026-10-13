# Northstar — Portfolio & Risk Analytics Platform

A responsive, full-stack portfolio analytics dashboard for tracking investment holdings, recording buy/sell transactions, reviewing portfolio performance, and exploring basic risk indicators. Built with **Python, Flask, SQLAlchemy, MySQL, HTML, CSS, and JavaScript**.

<p align="center">
  <img src="docs/screenshots/dashboard.png" alt="Northstar Portfolio and Risk Analytics dashboard preview" width="100%" />
</p>

<p align="center">
  <strong>Portfolio overview · Holdings · Transactions · Risk analysis · Reports & exports</strong>
</p>

> **Screenshot note:** The dashboard image is a presentation preview of the project's interface using illustrative demo values. The application itself calculates displayed metrics from the assets stored in your configured database. Demo holdings are fictional and are not live market data.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Getting Started](#getting-started)
- [Demo Data](#demo-data)
- [API Reference](#api-reference)
- [Risk Methodology](#risk-methodology)
- [Limitations and Disclaimer](#limitations-and-disclaimer)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

Northstar is an educational investment portfolio dashboard designed to make common portfolio information easier to review in one place. Users can manage assets, record purchases and sales, inspect allocation and concentration indicators, and export portfolio data for further analysis.

The frontend is served by Flask using a responsive HTML/CSS interface and JavaScript. Flask exposes JSON API routes, while Flask-SQLAlchemy persists assets and transaction history in MySQL.

## Features

### Portfolio dashboard

- Summary cards for total market value, cost basis, unrealized profit/loss (P&L), and weighted portfolio beta.
- Doughnut chart showing market value by asset class.
- Risk snapshot with holding count, number of asset classes, and largest sector.
- Top holdings table ordered by market value.

### Holdings management

- Add, edit, search, filter, and delete assets.
- Store ticker, asset name, asset class, sector, quantity, average cost, current price, and beta.
- Calculate market value, cost value, unrealized P&L, and P&L percentage from entered values.

### Transaction tracking

- Record `BUY` and `SELL` transactions with quantity, unit price, date, and optional notes.
- Buying updates holding quantity and weighted average cost.
- Selling reduces the holding quantity and rejects sales that exceed the current holding.
- Review recent transaction history.

### Risk analysis

- Calculate market-value-weighted beta.
- Show sector exposure and the largest sector's share of portfolio value.
- Show the largest holding's share of portfolio value.
- Include an explanation of the basic calculations and their limitations.

### Reports and exports

- Download holdings as CSV.
- Download transaction history as CSV from the Reports & Exports view.
- Copy a text summary of key portfolio indicators.

### Additional details

- Responsive navigation for desktop and smaller screens.
- Database health endpoint.
- Optional command for loading fictional sample holdings.
- Learning Resources link to an external investment banking training course.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask 3 |
| ORM / database access | Flask-SQLAlchemy, SQLAlchemy |
| Database | MySQL 8+ |
| MySQL driver | PyMySQL |
| Configuration | python-dotenv and `.env` |
| Frontend | HTML5, CSS3, JavaScript |
| Charting | Chart.js via CDN |
| API style | REST-like JSON endpoints |

## Project Structure

```text
portfolio_risk_analytics/
├── app.py                    # Flask app, models, API routes, demo seed command
├── requirements.txt          # Python dependencies
├── schema.sql                # MySQL database creation script
├── .env.example              # Example database configuration
├── README.md
├── templates/
│   └── index.html            # Dashboard and dialog markup
├── static/
│   ├── style.css             # Responsive UI styling
│   └── app.js                # API calls, rendering, forms, charts, exports
└── docs/
    └── screenshots/
        └── dashboard.png     # README dashboard preview
```

## Requirements

- Python **3.10 or newer**
- MySQL Server **8 or newer**
- MySQL Workbench (optional, useful for running `schema.sql`)
- A modern browser
- Internet access for the Chart.js and Google Fonts CDN assets used by the UI

## Getting Started

The steps below use Windows PowerShell. Commands can be adapted for macOS or Linux.

### 1. Clone the repository

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd portfolio_risk_analytics
```

Replace `<YOUR_GITHUB_REPOSITORY_URL>` with the URL of your GitHub repository. If you have already downloaded and extracted the project ZIP, open a terminal in the extracted `portfolio_risk_analytics` folder instead.

### 2. Create and activate a virtual environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, review your local execution policy or use Command Prompt instead:

```bat
.venv\Scripts\activate.bat
```

### 3. Install Python dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create the database

Start MySQL Server. Open `schema.sql` in MySQL Workbench and execute it. The script creates a database named `portfolio_risk_db`. The application defines the `assets` and `transactions` tables in `app.py` and creates them when the app starts.

### 5. Configure environment variables

Copy the example file:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and set `DATABASE_URL` to match your local MySQL username and password. For example:

```dotenv
DATABASE_URL=mysql+pymysql://root:YOUR_MYSQL_PASSWORD@localhost/portfolio_risk_db
```

Replace `YOUR_MYSQL_PASSWORD` with your actual local database password. URL-encode special characters in the password if needed. Never commit your real `.env` file or credentials to GitHub.

### 6. Start the application

From the project root, run:

```powershell
python app.py
```

Open the URL shown in the terminal, normally:

- **Application:** http://127.0.0.1:5000
- **Health check:** http://127.0.0.1:5000/api/health

Keep the terminal open while using the application. The dashboard requires a working database connection to load and save portfolio information.

### 7. (Optional) Load demo holdings

In a second terminal, activate the same virtual environment, move to the project root, and run:

```powershell
flask --app app seed-demo
```

The command inserts a small set of fictional sample holdings only when the assets table is empty. The example symbols and prices are for demonstration and are not live market data.

## API Reference

The following endpoints are implemented in `app.py`:

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/health` | Check whether the database connection is available |
| `GET` | `/api/summary` | Return portfolio totals, weighted beta, allocations, risk label, and top holdings |
| `GET` | `/api/assets` | List holdings; supports `q` search and `type` filtering query parameters |
| `POST` | `/api/assets` | Create a holding |
| `PUT` | `/api/assets/<id>` | Update a holding |
| `DELETE` | `/api/assets/<id>` | Delete a holding |
| `GET` | `/api/transactions` | Return up to 100 recent transactions |
| `POST` | `/api/transactions` | Record a `BUY` or `SELL` transaction and update holdings |
| `GET` | `/api/export/assets.csv` | Download holdings as a CSV file |

### Example health response

```json
{
  "status": "ok",
  "database": "connected"
}
```

For `POST` requests, send a JSON body with the fields expected by the relevant form. Asset creation requires `symbol`, `name`, `asset_type`, `sector`, `quantity`, `avg_cost`, `current_price`, and `beta`. Transaction creation requires a valid existing `symbol`, `transaction_type` (`BUY` or `SELL`), positive `quantity`, and positive `price`; `transaction_date` and `notes` are optional.

## Risk Methodology

- **Market value:** quantity × current price entered for the asset.
- **Cost value:** quantity × average cost entered for the asset.
- **Unrealized P&L:** market value − cost value.
- **P&L percentage:** unrealized P&L ÷ cost value × 100, when cost value is non-zero.
- **Weighted beta:** sum of each holding's market value × beta, divided by total portfolio market value.
- **Sector concentration:** market value of the largest sector ÷ total portfolio market value.
- **Largest position:** market value of the largest holding ÷ total portfolio market value.

These are simple educational indicators. The application does **not** currently calculate value at risk (VaR), historical volatility, correlation, drawdown, or portfolio returns from a historical market-price time series.

## Limitations and Disclaimer

- This is an educational portfolio analytics prototype, not a broker, trading platform, or financial adviser.
- Prices and beta values are manually entered or fictional demo inputs; the app does not fetch live market prices.
- Risk labels are simple heuristics based on weighted beta, not a comprehensive risk model.
- The app does not place trades, connect to brokerage accounts, or provide investment recommendations.
- The supplied learning link opens an external Uncodemy course page; it does not enroll the user from within this application.

Do not use this prototype as the sole basis for real investment decisions.

## Troubleshooting

**Database connection fails**

- Confirm that MySQL Server is running and `portfolio_risk_db` exists.
- Verify the username, password, host, and database name in `.env`.
- Ensure the password is URL-encoded if it contains URL-special characters.
- Open `/api/health` to inspect the connection status.

**The dashboard does not load chart data**

- Check the terminal for Flask errors and confirm `/api/summary` returns JSON.
- Verify your browser can access the Chart.js CDN, since the chart library is loaded externally.
- Confirm the database contains assets or run the optional demo seed command.

**`flask` command is not found**

- Activate the project's virtual environment and install dependencies with `pip install -r requirements.txt`.
- Alternatively, use the environment's Python executable to run Flask CLI commands.

## Future Enhancements

- Historical price imports and time-series performance charts
- Volatility, drawdown, correlation, and VaR analysis with clear assumptions
- Authentication and multi-user portfolios
- Unit and integration tests for transaction calculations and API validation
- Containerized deployment and CI checks
- More configurable reports and downloadable portfolio summaries

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Make a focused change and test it locally.
4. Commit with a descriptive message.
5. Open a pull request describing the change.

## License

No license file is currently included. Add a `LICENSE` file before presenting the project as open source, and update this section to match the chosen license.
