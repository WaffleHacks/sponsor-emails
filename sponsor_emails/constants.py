# The default configuration if none exists
DEFAULT_CONFIG = """{
  "credentials": {
    "gcp_service_account": "./service-account.json",
    "mailgun_domain": "",
    "mailgun_api_key": ""
  },
  "senders": {
    "url": "https://docs.google.com/spreadsheets/d/your-senders-sheet/edit",
    "sheet": "Organizers",
    "reply_to": "sponsors@your.domain",
    "header": "Name"
  },
  "sponsors": {
    "url": "https://docs.google.com/spreadsheets/d/your-sponsors-sheet/edit",
    "sheet": "Sponsorship Database",
    "headers": {
      "company_name": "Company Name",
      "contact_name": "Contact Name",
      "contact_email": "Contact Email"
    }
  },
  "template": {
    "url": "https://docs.google.com/document/d/your-document/edit",
    "placeholders": {
      "company_name": "{COMPANY}",
      "contact_name": "{RECIPIENT}",
      "sender_name": "{SENDER}"
    }
  }
}
"""

# GCP authentication scopes
SCOPES = [
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
]
