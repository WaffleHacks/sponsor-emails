import click
from email.utils import getaddresses
import gdoc
from googleapiclient.errors import HttpError
import gspread
from json import JSONDecodeError
import mailgun
import random
import typing as t
from uuid import uuid4

from .errors import CredentialsException, NotFoundException, SendException
from .. import logging, sheets
from ..config import Config, TemplatePlaceholders


def format_template(
    placeholders: TemplatePlaceholders, values: TemplatePlaceholders, template: str
) -> str:
    """
    Replace the values within a template
    :param placeholders: the placeholder names
    :param values: the values for each placeholder
    :param template: the template to format
    :return: a formatted template
    """
    for key in placeholders.__fields__.keys():
        placeholder = getattr(placeholders, key)
        value = getattr(values, key)

        template = template.replace(placeholder, value)

    return template


def send_message(
    mg: mailgun.MailGun,
    templates: t.Tuple[str, str],
    contact_name: str,
    contact_email: str,
    sender: str,
    reply_to: str,
    dry_run: bool,
) -> bool:
    """
    Send an individual email and report if it was successful
    :param mg: the MailGun instance
    :param templates: the text and html templates respectively
    :param contact_name: the name of the contact at the company
    :param contact_email: the email of the contact at the company
    :param sender: the name of the person sending the email
    :param reply_to: the email which replies are directed to
    :param dry_run: whether to actually send the email
    :return: whether the sending was successful
    """
    text, html = templates

    # Format the sender email
    sender_email = f"{sender[0]}{sender[sender.index(' ') + 1:].replace('-', '')}@{mg.domain}".lower()

    # Get and format the contact email(s)
    pairs = getaddresses([contact_email.replace(" ", "")])
    emails = []
    for _, email in pairs:
        if email == "":
            logging.error(f'invalid email address found in "{contact_email}"')
            return False
        emails.append(f"{contact_name} <{email.lower()}>")

    # Print out the content on dry runs
    if dry_run:
        click.echo(
            f"To: {', '.join(emails)}\n"
            f"From: {sender} <{sender_email}>\n"
            f"Subject: WaffleHacks Sponsorship Opportunity\n"
            f"Reply To: {reply_to}\n\n\n"
            f"{text}",
            file=open(f"./dry-run-out/{contact_name} - {uuid4()}", "w"),
        )
        return True

    try:
        mg.send(
            from_=f"{sender} <{sender_email}>",
            to=emails,
            subject="WaffleHacks Sponsorship Opportunity",
            text=text,
            html=html,
            headers={"Reply-To": reply_to},
        )
    except mailgun.MailGunException as e:
        logging.error(f"failed to send message: {e}")
        return False

    return True


def run(
    cfg: Config, single: bool, dry_run: bool, overwrite: t.Optional[str]
) -> t.Tuple[int, int, int]:
    """
    Send all the sponsor emails
    :param cfg: the configuration
    :param single: send only a single email
    :param dry_run: don't actually send any emails
    :param overwrite: replace the recipient email
    :return: the number of successful emails, number of skipped emails, and total emails sent
    """
    # Connect to the services
    logging.info("Connecting to Google Drive and Mailgun...")
    try:
        gd = gdoc.authorize(cfg.credentials.gcp())
        gs = gspread.authorize(cfg.credentials.gcp())
        mg = mailgun.authorize(
            cfg.credentials.mailgun(), cfg.credentials.mailgun_domain
        )
    except (JSONDecodeError, KeyError, ValueError) as e:
        raise CredentialsException(f"unable to load credentials: {e}")

    # Open the documents
    try:
        logging.info("Opening message template...")
        template = gd.open_by_url(cfg.template.url)
        template_text = template.text
        template_html = template.html

        logging.info("Opening senders list...")
        senders = gs.open_by_url(cfg.senders.url).worksheet(cfg.senders.sheet)
        logging.info("Opening sponsors list...")
        sponsors = gs.open_by_url(cfg.sponsors.url).worksheet(cfg.sponsors.sheet)
    except gspread.exceptions.APIError as e:
        if e.response.status_code == 404:
            raise NotFoundException("could not find sheet")

        error = e.response.json()
        raise SendException(error.get("message"))
    except gspread.exceptions.WorksheetNotFound as e:
        raise NotFoundException(f'could not find worksheet "{e.args[0]}"')
    except HttpError as e:
        if e.status_code == 404:
            raise NotFoundException("could not find template")
        else:
            raise SendException(
                f"unable to get document: ({e.status_code}) {e._get_reason()}"
            )
    except (gdoc.NoValidIdFound, gspread.exceptions.NoValidUrlKeyFound):
        raise SendException("invalid document url")

    # Get the columns
    try:
        sponsors_columns = sheets.map_columns_to_headers(sponsors, cfg.sponsors.headers)
        senders_column = sheets.index_to_label(
            senders.row_values(1).index(cfg.senders.header)
        )
    except (ValueError, sheets.MissingHeaderException):
        raise NotFoundException("could not find column header")

    # Fetch the data
    logging.info("Fetching sponsors data...")
    sponsors_data = sheets.fetch_data(
        sponsors, list(sponsors_columns.dict().values()), single
    )
    logging.info("Fetching senders data...")
    senders_data = sheets.fetch_data(senders, [senders_column])
    senders_data = senders_data[senders_column]  # Get the bare array

    # Ensure all data is the same length
    print(sponsors_data)
    lengths = list(map(lambda d: len(d), sponsors_data.values()))
    total = lengths[0]
    if not lengths.count(lengths[0]) == len(lengths):
        raise SendException("all sponsor data columns must be the same length")

    # Check that the user REALLY wants to send emails
    click.confirm(
        f"Are you sure you want to send {click.style(total, fg='red')} sponsor emails?",
        abort=True,
    )

    # Send all the messages
    success = 0
    skipped = 0
    logging.info(f"Sending {total} messages...")
    for i in range(total):
        # Get all the values from the spreadsheet
        company = sponsors_data[sponsors_columns.company_name][i]
        contact_name = sponsors_data[sponsors_columns.contact_name][i]
        contact_email = sponsors_data[sponsors_columns.contact_email][i]
        sent_status = sponsors_data[sponsors_columns.sent_status][i]
        sender = random.choice(senders_data)

        status = f"<{i + 1}/{total}> {{}} message to {company} ({contact_name})"

        # Only send if no status
        if sent_status != cfg.sponsors.statuses.pending:
            logging.info(status.format("already sent"))
            success += 1
            continue

        # Ensure all the necessary data is present
        if company is None or contact_name is None or contact_email is None:
            logging.error(
                f'missing value at least one of "company_name", "contact_name", "contact_email"'
                f" for row: {company}, {contact_name}, {contact_email}"
            )
            logging.error(status.format("failed to send"))
            skipped += 1
            continue

        placeholder_values = TemplatePlaceholders(
            company_name=company, contact_name=contact_name, sender_name=sender
        )

        # Format the templates
        html = format_template(
            cfg.template.placeholders, placeholder_values, template_html
        )
        text = format_template(
            cfg.template.placeholders, placeholder_values, template_text
        )

        # Attempt to send the message
        if send_message(
            mg,
            (text, html),
            contact_name,
            contact_email if overwrite is None else overwrite,
            sender,
            cfg.senders.reply_to,
            dry_run,
        ):
            logging.info(status.format("sent"))
            success += 1
        else:
            logging.error(status.format("failed to send"))
            skipped += 1

    return success, skipped, total
