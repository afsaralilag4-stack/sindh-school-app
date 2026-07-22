# sindh-school-app
# 🏫 Sindh Government Primary School Portal

A Streamlit-based School Management Portal for Government Primary Schools in Sindh.

## Features

- 🔐 Secure Login System
- 👨‍🏫 Role-Based Access (Principal & Teacher)
- 📖 Digital General Register (GR)
- 📅 Teacher Leave Management
- 📢 Official Circulars
- 📊 Daily School Reporting
- ☁️ Google Sheets Database
- 🚀 Streamlit Cloud Ready

---

# Project Structure

```
sindh-school-app/
│
├── app.py
├── requirements.txt
├── README.md
└── .streamlit/
    └── secrets.toml
```

---

# Requirements

```
streamlit
pandas
st-gsheets-connection
gspread
google-auth
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Google Sheets Setup

Create a Google Spreadsheet with the following worksheets:

## 1. Users

| Username | Password | Role | Full_Name |
|----------|----------|------|-----------|
| admin | admin123 | Principal | Ali Ahmed |
| teacher1 | 12345 | Teacher | Sara Khan |

---

## 2. Student_GR

| GR_No | Student_Name | Father_Name | Class |
|-------|--------------|-------------|-------|
| 1 | Ahmed | Karim | 1 |
| 2 | Ayesha | Saleem | 2 |

---

## 3. Teacher_Leave

| Teacher | Leave_Type | Start_Date | End_Date | Reason | Status |
|----------|------------|------------|----------|---------|--------|

---

## 4. Circulars

| Date | Subject | Content | File_Link |
|------|----------|---------|-----------|

---

# Google Service Account

1. Open Google Cloud Console
2. Create a Project
3. Enable:

- Google Sheets API
- Google Drive API

4. Create a Service Account.
5. Download the JSON key.
6. Share your Google Sheet with the service account email as **Editor**.

Example:

```
school-project@school-project.iam.gserviceaccount.com
```

---

# Streamlit Secrets

Create:

```
.streamlit/secrets.toml
```

Example:

```toml
[connections.gsheets]

spreadsheet = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"

type = "service_account"
project_id = "YOUR_PROJECT_ID"
private_key_id = "YOUR_PRIVATE_KEY_ID"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
client_email = "YOUR_SERVICE_ACCOUNT_EMAIL"
client_id = "YOUR_CLIENT_ID"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "YOUR_CLIENT_CERT_URL"
```

---

# Run the Project

```bash
streamlit run app.py
```

---

# Deploy to Streamlit Community Cloud

1. Push the project to GitHub.
2. Go to Streamlit Community Cloud.
3. Connect your GitHub repository.
4. Deploy the app.
5. Open **App Settings → Secrets**.
6. Paste the contents of your `secrets.toml`.
7. Save and restart the app.

---

# Default User Example

Username:

```
admin
```

Password:

```
admin123
```

Role:

```
Principal
```

---

# Technologies Used

- Python
- Streamlit
- Pandas
- Google Sheets
- Google Cloud Service Account

---

# License

This project is intended for educational use in Government Primary Schools, Sindh.

Developed using Python and Streamlit.
