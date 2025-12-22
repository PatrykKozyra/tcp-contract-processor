# TCP Contract Processor - Setup Guide

Complete step-by-step guide to set up and run the application.

## Prerequisites

- Python 3.8 or higher installed
- Anthropic API key (get from https://console.anthropic.com/)

## Step-by-Step Setup

### Step 1: Open Terminal/Command Prompt

**Windows:**
- Press `Win + R`
- Type `cmd` and press Enter
- Or use PowerShell or Windows Terminal

**Mac/Linux:**
- Open Terminal application

### Step 2: Navigate to Project Directory

```bash
cd c:\Users\serav\Documents\CODE\tc-agent-project
```

Verify you're in the correct directory:
```bash
dir     # Windows
ls      # Mac/Linux
```

You should see files like `streamlit_app.py`, `requirements.txt`, etc.

### Step 3: Create Virtual Environment

**Windows (Command Prompt):**
```bash
python -m venv venv
```

**Windows (PowerShell):**
```bash
python -m venv venv
```

**Mac/Linux:**
```bash
python3 -m venv venv
```

This creates a folder called `venv` in your project directory.

### Step 4: Activate Virtual Environment

**Windows (Command Prompt):**
```bash
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

If you get an error about execution policies in PowerShell, run this first:
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

**Success indicator:** You'll see `(venv)` at the beginning of your command prompt:
```
(venv) C:\Users\serav\Documents\CODE\tc-agent-project>
```

### Step 5: Upgrade pip (Optional but Recommended)

```bash
python -m pip install --upgrade pip
```

### Step 6: Install Requirements

Install all dependencies from requirements.txt:

```bash
pip install -r requirements.txt
```

You'll see output like:
```
Collecting anthropic...
Collecting pdfplumber...
Collecting pandas...
...
Successfully installed anthropic-... pdfplumber-... pandas-... openpyxl-... streamlit-...
```

**Verify installation:**
```bash
pip list
```

You should see all the packages listed.

### Step 7: Set Up Environment Variables

Create a `.env` file in the project directory:

**Windows:**
```bash
echo ANTHROPIC_API_KEY=your_api_key_here > .env
```

**Mac/Linux:**
```bash
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env
```

Or manually create the file:
1. Create a new file named `.env` (note the dot at the beginning)
2. Add this line:
   ```
   ANTHROPIC_API_KEY=your_actual_api_key_here
   ```
3. Save the file

**Important:** Replace `your_actual_api_key_here` with your real Anthropic API key.

### Step 8: Run the Streamlit App

```bash
streamlit run streamlit_app.py
```

**What happens:**
1. Streamlit starts a local web server
2. Your browser automatically opens to `http://localhost:8501`
3. You'll see the TCP Contract Processor interface

**Terminal output will look like:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### Step 9: Use the Application

1. The web interface opens in your browser
2. Go to "Upload & Process" tab
3. Upload PDF files from the `sample_contracts` folder
4. Click "🚀 Process Contracts"
5. View results in "View & Search" tab

### Step 10: Stop the Application

To stop the Streamlit server:
- Press `Ctrl + C` in the terminal
- Confirm with `Y` if prompted

### Step 11: Deactivate Virtual Environment

When you're done working:

```bash
deactivate
```

The `(venv)` prefix disappears from your prompt.

## Quick Reference - Common Commands

### Starting the App (After Initial Setup)

```bash
# 1. Navigate to project
cd c:\Users\serav\Documents\CODE\tc-agent-project

# 2. Activate virtual environment
venv\Scripts\activate.bat          # Windows CMD
venv\Scripts\Activate.ps1          # Windows PowerShell
source venv/bin/activate           # Mac/Linux

# 3. Run Streamlit
streamlit run streamlit_app.py
```

### Alternative: Command-Line Interface

If you prefer CLI instead of web UI:

```bash
# Interactive menu
python tcp_cli.py

# Process single file
python tcp_cli.py --process tcp_contract_001.pdf

# Process all files
python tcp_cli.py --process-all

# Query vessel
python tcp_cli.py --query "Pacific Star"

# Export to Excel
python tcp_cli.py --export contracts.xlsx
```

## Troubleshooting

### Problem: "python is not recognized"

**Solution:**
- Python is not installed or not in PATH
- Try `python3` instead of `python`
- Or `py` instead of `python`
- Reinstall Python and check "Add to PATH" during installation

### Problem: "No module named 'streamlit'"

**Solution:**
- Virtual environment not activated
- Run: `venv\Scripts\activate.bat`
- Then: `pip install -r requirements.txt`

### Problem: PowerShell execution policy error

**Solution:**
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate again:
```bash
venv\Scripts\Activate.ps1
```

### Problem: "ANTHROPIC_API_KEY not found"

**Solution:**
- Check `.env` file exists in project root
- Verify it contains: `ANTHROPIC_API_KEY=your_key`
- No spaces around the `=` sign
- No quotes needed around the key

### Problem: Streamlit won't open in browser

**Solution:**
- Manually open: `http://localhost:8501`
- Check firewall isn't blocking port 8501
- Try: `streamlit run streamlit_app.py --server.port 8502`

### Problem: Can't find sample contracts

**Solution:**
- PDFs should be in `sample_contracts/` folder
- Check path: `c:\Users\serav\Documents\CODE\tc-agent-project\sample_contracts\`
- Generate PDFs first: `python generate_pdfs.py`

## File Structure

After setup, your project should look like:

```
tc-agent-project/
├── venv/                          # Virtual environment (created in setup)
├── .env                           # API key (created in setup)
├── streamlit_app.py               # Web UI
├── tcp_cli.py                     # Command-line interface
├── requirements.txt               # Dependencies
├── generate_pdfs.py               # Generate sample contracts
├── src/
│   ├── main.py                    # Core processing
│   └── data_standardization.py   # Data standardization
├── sample_contracts/              # PDF contracts
│   ├── tcp_contract_001.pdf
│   ├── tcp_contract_002.pdf
│   └── tcp_contract_003.pdf
└── output/                        # Exported files
```

## Next Steps

1. **Generate sample PDFs** (if not already done):
   ```bash
   python generate_pdfs.py
   ```

2. **Test with a single contract:**
   ```bash
   streamlit run streamlit_app.py
   ```
   Then upload `sample_contracts/tcp_contract_001.pdf`

3. **Process all contracts:**
   - Upload all 3 PDFs at once
   - Click "Process Contracts"
   - View in "View & Search" tab

4. **Export data:**
   - Click "Download as Excel"
   - Open in Excel/Google Sheets

## Additional Resources

- **Streamlit Guide**: See [STREAMLIT_GUIDE.md](STREAMLIT_GUIDE.md)
- **CLI Guide**: See [CLI_README.md](CLI_README.md)
- **Anthropic API**: https://docs.anthropic.com/

## Daily Workflow

Every time you want to use the app:

1. Open terminal
2. Navigate to project: `cd c:\Users\serav\Documents\CODE\tc-agent-project`
3. Activate venv: `venv\Scripts\activate.bat`
4. Run app: `streamlit run streamlit_app.py`
5. When done: `Ctrl+C` to stop, `deactivate` to exit venv

That's it! You're ready to process TCP contracts. 🚢
