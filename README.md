# Sponsor Emails
Automatically send sponsorship emails using Google Docs, Google Sheets, and [MailGun](https://www.mailgun.com).


## Installation & Usage

`sponsor-emails` can be downloaded as a Python package from the [Actions](https://github.com/WaffleHacks/sponsor-emails/actions) tab, or it can be installed directly with Pip.

```shell
# Pip from source
pip install git+https://github.com/WaffleHacks/sponsor-emails.git

# Pip from downloaded wheel
pip install ~/Downloads/sponsor_emails_3.9.whl

# Running
sponsor-emails --help
```

You can also use [Pipx](https://pypa.github.io/pipx/) to install and run `sponsor-emails` in a virtual environment.

```shell
pipx run --spec git+https://github.com/WaffleHacks/sponsor-emails.git sponsor-emails --help
```

### Configuration

Once you have `sponsor-emails` installed, run `sponsor-emails validate` to generate the default configuration.
This should error as there are some necessary details you will need to fill in, such as your GCP and MailGun credentials.

#### GCP Service Account

1. Register for a [Google Cloud Platform](https://console.cloud.google.com/) account, if you don't already have on
1. Enable the APIs for Google Docs, Google Drive, and Google Sheets
    1. Navigate to the [APIs & Services page](https://console.cloud.google.com/apis/dashboard)
    1. Click on "Enable APIs and Services" near the top
    1. Search for and enable the "Google Docs API", "Google Drive API", and "Google Sheets API"
1. Create a [Service Account](https://cloud.google.com/iam/docs/service-accounts) to access the APIs with
    1. Navigate to ["Credentials"](https://console.cloud.google.com/apis/credentials) on the APIs & Services page
    1. Click on "Create Credentials" near the top and select "Service account"
    1. Fill out the name, id, and, optionally, the description; then click "Done"
    1. Click on "Manage service accounts" on the right by the "Service Accounts" header
    1. Click the three dots (`⋮`) near your recently created service account and select "Manage keys"
    1. Click on "Add Key", then select "Create new key" and use the JSON format
    1. Save the downloaded key somewhere safe and remember its location for later
1. Share any Google Docs or Google Sheets with the service account's email using the standard "Share" button
1. Copy the path to the service account file into the `credentials.gcp` in `config.json` field. Ex:
```json
{
   "credentials": {
      "gcp": "/path/to/your/service-account.json"
   }
}
```
    

#### MailGun API Access

1. Register for a [MailGun](https://signup.mailgun.com/new/signup) account, if you don't already have one
1. Add your domain if you haven't already, following the [offical docs](https://documentation.mailgun.com/en/latest/user_manual.html#verifying-your-domain)
    - You can use the automatically added sandbox domain, but it should only be used for testing
1. Get your private API key from the "API Keys" page
   1. Go to the ["API Keys"](https://app.mailgun.com/app/account/security/api_keys) page under "Settings" in the sidebar
   1. Copy the key under "Private API key"
1. Paste the API key and domain into `config.json` at `credentials.mailgun_api_key` and `credentials.mailgun_domain` respectively. Ex:
```json
{
   "credentials": {
      "mailgun_domain": "your.domain.com",
      "mailgun_api_key": "afffeag-your-api-key-afgjo"
   }
}
```

#### Documents and Sheets

1. Configure the template document
   1. Copy the URL for your Google Doc and paste it into `template.url`
   1. Add your placeholders for the company's name, contact's name, and sender's name under `template.placeholders`. These are all case-sensitive.
1. Configure the sponsors spreadsheet
   1. Copy the URL for your Google Sheet and paste it into `sponsors.url`
   1. Put the name of the worksheet (ex. "Sheet 1") into `sponsors.sheet`
   1. Put the statuses for your messages into `sponsors.statuses`.
      - The `sponsors.statuses.sent` will be set when a message gets successfully sent
      - The `sponsors.statuses.pending` will be set when a message fails to send
      - If the status is not equal to `sponsors.statuses.pending` before sending, the message will not be sent
   1. Set the column headers in `sponsors.headers` to the respective columns in your spreadsheet
   1. If you have a sponsorship package ([example](https://wafflehacks.tech/static/1528e567aba053864433e680580f90d0/sponsorship-package.pdf)), put copy the path to `sponsors.package`, otherwise set it to `null`
1. Configure the senders spreadsheet
   1. Copy the URL for your Google Sheet and paste it into `senders.url`
   1. Put the name of the worksheet (ex. "Sheet 2") into `senders.sheet`
   1. Set `senders.header` to the name of the column with the organizer's first and last names
   1. Set `senders.reply_to` to the email that messages should reply to


#### Validation

To ensure your configuration is correct, run `sponsor-emails validate`.
