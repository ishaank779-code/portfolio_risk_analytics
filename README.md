# Northstar — Portfolio & Risk Analytics Platform

<p align="center">
  <strong>A full-stack dashboard for portfolio tracking, holdings management, transaction history, and basic investment risk indicators.</strong>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" />
  <img alt="Flask" src="https://img.shields.io/badge/Flask-3.x-000000?logo=flask&logoColor=white" />
  <img alt="MySQL" src="https://img.shields.io/badge/MySQL-8%2B-4479A1?logo=mysql&logoColor=white" />
  <img alt="JavaScript" src="https://img.shields.io/badge/JavaScript-ES6%2B-F7DF1E?logo=javascript&logoColor=black" />
  <img alt="License" src="https://img.shields.io/badge/License-Not%20specified-lightgrey" />
</p>

<p align="center">
  <img src="docs/screenshots/dashboard.png" alt="Northstar Portfolio and Risk Analytics dashboard preview" width="100%" />
</p>

<p align="center">
  <strong>Portfolio Overview · Holdings · Transactions · Risk Analysis · Reports & Exports</strong>
</p>

> **Preview note:** The image above is a presentation preview with illustrative demo values. The running application calculates its metrics from records in your configured database. Demo holdings are fictional and are not live market data.

---

## 📌 Project Overview

**Northstar — Portfolio & Risk Analytics Platform** is an educational, full-stack web application that helps users organize investment holdings, record buy/sell transactions, review portfolio values, and inspect basic risk indicators in one dashboard.

The frontend uses responsive HTML, CSS, and JavaScript. A Python Flask server provides JSON API routes, and Flask-SQLAlchemy stores assets and transaction history in MySQL.

## ✨ Key Features

### 📊 Portfolio Dashboard
- Summary cards for total market value, cost basis, unrealized profit/loss (P&L), and market-value-weighted beta.
- Doughnut chart showing portfolio value by asset class.
- Risk snapshot including holding count, asset-class count, and largest sector.
- Top holdings table ordered by market value.

### 🧾 Holdings Management
- Add, edit, search, filter, and delete holdings.
- Store ticker, asset name, asset class, sector, quantity, average cost, current price, and beta.
- Calculate market value, cost value, unrealized P&L, and P&L percentage from entered values.

### 🔁 Transaction Tracking
- Record `BUY` and `SELL` transactions with quantity, unit price, date, and optional notes.
- Buying updates holding quantity and weighted average cost.
- Selling reduces holding quantity and prevents selling more units than are held.
- Review recent transaction history.

### ⚠️ Risk Analysis
- Calculate market-value-weighted beta.
- Review sector exposure and largest-sector concentration.
- Review the largest holding's share of total portfolio value.
- Display basic calculation explanations and limitations.

### 📁 Reports & Exports
- Export holdings to CSV.
- Export transaction history to CSV from the Reports & Exports interface.
- Copy a text summary of key portfolio indicators.

### 🧩 Other Features
- Responsive layout for desktop and smaller screens.
- Database health-check endpoint.
- Optional command to load fictional demo holdings.

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| ORM / Database access | Flask-SQLAlchemy, SQLAlchemy |
| Database | MySQL 8+ |
| MySQL driver | PyMySQL |
| Configuration | python-dotenv, `.env` |
| Frontend | HTML5, CSS3, JavaScript |
| Charts | Chart.js via CDN |
| API | REST-style JSON endpoints |
| Version control | Git and GitHub |

## 📂 Project Structure

```text
portfolio_risk_analytics/
├── app.py                       # Flask app, models, API routes, demo seed command
├── requirements.txt             # Python dependencies
├── schema.sql                   # MySQL database creation script
├── .env.example                 # Example environment configuration
├── README.md
├── templates/
│   └── index.html               # Dashboard and dialog markup
├── static/
│   ├── style.css                # Responsive UI styles
│   └── app.js                   # API calls, UI rendering, forms, charts, exports
└── docs/
    └── screenshots/
        └── dashboard.png        # README dashboard preview
```

## ⚙️ Requirements

- Python 3.10 or newer
- MySQL Server 8 or newer
- MySQL Workbench (optional, for executing `schema.sql`)
- A modern web browser
- Internet access for Chart.js and Google Fonts assets loaded from CDNs

## 🚀 Installation & Setup (Windows)

### 1. Get the project

If you have cloned the GitHub repository:

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd portfolio_risk_analytics
```

Replace `<YOUR_GITHUB_REPOSITORY_URL>` with your repository URL. If you downloaded the ZIP instead, extract it and open a terminal in the `portfolio_risk_analytics` project folder.

### 2. Create and activate a virtual environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If you use Command Prompt instead of PowerShell, activate it with:

```bat
.venv\Scripts\activate.bat
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create the MySQL database

1. Start MySQL Server.
2. Open `schema.sql` in MySQL Workbench.
3. Execute the script to create the `portfolio_risk_db` database.
4. The application defines the `assets` and `transactions` tables in `app.py` and creates them when the app starts.

### 5. Configure environment variables

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and configure your local MySQL connection. Example:

```dotenv
DATABASE_URL=mysql+pymysql://root:YOUR_MYSQL_PASSWORD@localhost/portfolio_risk_db
```

Replace `YOUR_MYSQL_PASSWORD` with your own MySQL password. URL-encode special characters in the password if necessary. **Never commit `.env` or real credentials to GitHub.**

### 6. Run the application

From the project root, run:

```powershell
python app.py
```

Open the address printed in your terminal, normally:

- **Application:** http://127.0.0.1:5000
- **Health check:** http://127.0.0.1:5000/api/health

Keep the terminal open while using the dashboard. A working MySQL connection is required to load and save portfolio information.

### 7. (Optional) Load sample holdings

Open a second terminal in the project folder, activate the virtual environment, then run:

```powershell
flask --app app seed-demo
```

This inserts fictional sample holdings only if the assets table is empty. The example symbols and prices are not live market data.

## 🔌 API Reference

The following routes are implemented in `app.py`:

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/health` | Check whether the database is reachable |
| `GET` | `/api/summary` | Return portfolio totals, weighted beta, allocations, risk label, and top holdings |
| `GET` | `/api/assets` | List holdings; supports `q` search and `type` filtering query parameters |
| `POST` | `/api/assets` | Create a holding |
| `PUT` | `/api/assets/<id>` | Update a holding |
| `DELETE` | `/api/assets/<id>` | Delete a holding |
| `GET` | `/api/transactions` | Return up to 100 recent transactions |
| `POST` | `/api/transactions` | Record a `BUY` or `SELL` transaction and update holdings |
| `GET` | `/api/export/assets.csv` | Download holdings as CSV |

### Example health-check response

```json
{
  "status": "ok",
  "database": "connected"
}
```

For exact request fields and responses, inspect the API handlers in `app.py`. Asset creation expects fields such as `symbol`, `name`, `asset_type`, `sector`, `quantity`, `avg_cost`, `current_price`, and `beta`. Transaction creation uses an existing `symbol`, `transaction_type` (`BUY` or `SELL`), positive `quantity`, and positive `price`; date and notes are optional.

## 📐 Risk Calculation Methodology

- **Market value:** quantity × current price entered for an asset.
- **Cost value:** quantity × average cost entered for an asset.
- **Unrealized P&L:** market value − cost value.
- **P&L percentage:** unrealized P&L ÷ cost value × 100, when cost value is non-zero.
- **Weighted beta:** sum of each holding's market value × beta, divided by total portfolio market value.
- **Sector concentration:** market value of the largest sector ÷ total portfolio market value.
- **Largest position:** market value of the largest holding ÷ total portfolio market value.

These are simplified educational indicators. The application does **not** currently calculate value at risk (VaR), historical volatility, correlation, drawdown, or portfolio returns from historical market-price data.

## 🔒 Limitations & Disclaimer

- This is an educational portfolio analytics prototype, not a broker, trading platform, or financial adviser.
- Prices and beta values are manually entered or fictional demo inputs; live market prices are not fetched.
- Risk labels are simple heuristics based on weighted beta, not a comprehensive risk model.
- The app does not place trades, connect to brokerage accounts, or provide investment recommendations.
- The Learning Resources link opens an external Uncodemy course page; it does not enroll users from within this application.

Do not use this prototype as the sole basis for real investment decisions.

## 🧰 Troubleshooting

**Database connection fails**
- Confirm MySQL Server is running and `portfolio_risk_db` exists.
- Verify username, password, host, and database name in `.env`.
- URL-encode special characters in the password if needed.
- Check `http://127.0.0.1:5000/api/health`.

**Dashboard or charts show no data**
- Check the Flask terminal for errors.
- Confirm `/api/summary` returns JSON.
- Ensure the database contains holdings, or run the optional demo seed command.
- Confirm your browser can reach the Chart.js CDN.

**`flask` command is not found**
- Activate the project's virtual environment and install dependencies using `pip install -r requirements.txt`.

## 🛣️ Future Enhancements

- Historical price imports and time-series performance charts
- Volatility, drawdown, correlation, and VaR analysis with documented assumptions
- Authentication and multi-user portfolios
- Unit and integration tests for transaction calculations and API validation
- Containerized deployment and continuous integration checks
- Configurable reports and downloadable portfolio summaries

## 🤝 Contributing

1. Fork the repository.
2. Create a feature branch.
3. Make a focused change and test it locally.
4. Commit with a descriptive message.
5. Open a pull request describing your changes.

## 📄 License

No license file is currently included. Add a `LICENSE` file before distributing the project as open source, and update this section to match the license you choose.

---

<p align="center">
  Made for learning and demonstrating portfolio analytics workflows.
</p>
