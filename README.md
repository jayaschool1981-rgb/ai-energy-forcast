# ⚡ AI-Powered Building Energy Forecast Console

Welcome to the **Building Energy Forecast Console**! This application is a full-stack, intelligence-driven platform designed to predict future electricity consumption in commercial buildings. 

This document explains the project, the business problem it solves, its inner workings, and how to run it—**written entirely in plain, non-technical English.**

---

## 💡 The Core Problem: Energy Waste in Buildings
Commercial buildings are among the largest consumers of electricity in the world. Much of this energy is wasted because heating, ventilation, air conditioning (HVAC), and lighting systems operate on fixed schedules. They do not know in advance how much power they will actually need.

Energy needs change based on two primary factors:
1. **Time Factors:** Daily human routines (e.g., peak working hours vs. weekends or nights).
2. **Weather Factors:** The outside temperature (e.g., high heat requires air conditioning).

By predicting **future electricity demand (in kilowatt-hours, or kWh)** based on the time and temperature, building managers can optimize HVAC schedules, reduce waste, and save thousands of dollars on utility bills.

---

## 🧠 How the System Works (The 3 Core Layers)

The application acts like a miniature digital building coordinator split into three layers:

```
[ Web Dashboard ]  <--->  [ Intermediary Engine ]  <--->  [ The AI Brain ]
(Visual Screens)            (FastAPI Server)             (Math Forecast Weights)
                                   |
                                   v
                           [ Secure Database ]
                           (Postgres / SQLite)
```

### 1. The Visual Dashboard (Frontend)
The web page that you see in your browser. It contains:
* **The Controls:** Inputs for selecting a date/time and setting a target temperature.
* **The Analytics Chart:** A custom graph showing how predicted energy needs change over time.
* **Key Performance indicators (KPIs):** Real-time summaries displaying the last prediction, rolling averages, and peak electricity loads.

### 2. The Intermediary Engine (Backend API)
A silent background worker that listens for requests from the web dashboard, passes them to the AI Brain, records the results into a database log, and sends the answer back to your screen in milliseconds.

### 3. The AI Brain (Machine Learning Model)
A trained mathematical formula (specifically a **Neural Network**) that has analyzed months of building logs. 
* Unlike traditional programs with hardcoded rules, this Brain has learned the complex relationship between time, temperature, and electricity usage.
* When you give it a timestamp (e.g., *Friday at 2:00 PM in July*) and a temperature (e.g., *30°C*), it does the math and outputs the estimated energy load.

---

## 🔒 Enterprise Hardening: What makes this version secure and fast?
We upgraded the codebase to meet industry-grade standards so that it can handle millions of users and resist online attacks:

* **Executable File Protection (Pickle to NumPy):** Previously, the AI model was saved in a format that could let hackers run malicious scripts on the server. We converted the model weights into a secure, math-only format (`.npz` weights archive) that only runs safe equations.
* **Database Contention Safety:** Standard databases can lock up and crash if multiple users try to write logs at the same second. We implemented advanced "connection queues" (SQLAlchemy connection pooling) so the database coordinates many inputs simultaneously without freezing.
* **The Access Lock (API Key Authentication):** A digital lock protects the system. Users must present a validation key to call predictions, keeping compute resources safe from unauthorized public access.
* **Overload Guard (Rate Limiting):** A security guard monitors requests. If a single computer tries to spam the server with thousands of requests to crash it, the server blocks them, keeping the application online for everyone else.

---

## 🚀 How to Run the Application (Step-by-Step)

You do not need to install complex programming tools (like Python or Node.js) on your computer. You only need **Docker**, which bundles the entire system into self-contained packages.

### Step 1: Install Docker Desktop
1. Download and install **Docker Desktop** for your computer:
   👉 [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Open Docker Desktop and verify that it is running in the background.

### Step 2: Open Terminal / Command Prompt
- **On Windows:** Press the Windows Key, type **PowerShell** or **Command Prompt**, and open it.
- Navigate to the folder where you downloaded this project. For example:
  ```powershell
  cd D:\Om_Personal_workspace\ai-energy-forcast
  ```

### Step 3: Start the Application
Copy and paste the command below into your terminal and press **Enter**:
```bash
docker-compose up --build
```
*Wait a couple of minutes. Docker will automatically assemble the database, start the API engine, compile the web dashboard, and launch the service.*

---

## 🎮 How to Use the Dashboard

1. **Access the web address:** Open your browser and go to:  
   👉 [http://localhost](http://localhost)
2. **Unlock the screen:** The dashboard is protected. Copy the token key below, paste it into the **X-API-Key** input field, and click **Authorize Console**:
   ```text
   enterprise-telemetry-token-2026
   ```
3. **Generate Forecasts:** Once unlocked, choose any date/time and input a temperature (e.g., `30.0`), then click **Run Inference** to watch the charts and prediction readouts populate.
4. **Shut down:** To turn off the application, go back to your command window and press `Ctrl + C`.
