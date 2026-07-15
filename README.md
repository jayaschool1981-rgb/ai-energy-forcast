# ⚡ AI-Powered Building Energy Forecast Console

This application predicts future building electricity usage (in kWh) based on a timestamp and ambient temperature parameters. It uses a secure Machine Learning model (Neural Network) running on a full-stack platform.

---

## 🚀 How to Run the Project (Easy Mode)

If you are a non-technical user, the easiest way to run the entire application (including the database, caching systems, backend, and user interface) is by using **Docker Desktop**.

### Step 1: Install Docker Desktop (If not installed)
1. Download and install **Docker Desktop** for your operating system:
   👉 [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Open Docker Desktop and make sure it is running in the background.

### Step 2: Open Terminal / Command Prompt
- On Windows: Search for **PowerShell** or **Command Prompt** in the Start Menu and open it.
- Navigate to this project folder.

### Step 3: Run the Startup Command
Copy and paste the following command into your terminal and press **Enter**:
```bash
docker-compose up --build
```
*This command will automatically download everything needed, build the application containers, and start both the backend API and the user dashboard.*

---

## 💻 How to Access and Use the Application

Once the command finishes running, you can access the application from your web browser:

1. **Open the User Interface:**
   Type the following address into your web browser (Chrome, Edge, Safari):
   👉 [http://localhost:80](http://localhost) (or just `http://localhost`)

2. **Unlock the Console (Access Key):**
   The application is secured. When prompted, enter the following Access Token to unlock it:
   ```text
   enterprise-telemetry-token-2026
   ```
   Click **Authorize Console**.

3. **Run a Prediction:**
   - Change the **Ambient Temperature** (e.g., set to `28.5` degrees).
   - Click **Run Inference**.
   - The predicted electricity usage will display on the screen, and the history table and line chart will update instantly.

---

## 🛠️ Stopping the Application
To shut down the servers, go back to your terminal window and press:
- `Ctrl + C` (on Windows/Linux) or `Cmd + .` (on Mac).
