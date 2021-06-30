import click
from pathlib import Path
from pydantic import ValidationError
from sys import exit
from typing import Optional

from sponsor_emails import Config, logger, sender, tests


@click.group(
    name="sponsor-emails",
    help="Automate sending sponsorship emails using Google Docs, Google Sheets, and MailGun",
)
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
        allow_dash=False,
        path_type=Path,
    ),
    help="Configuration file to load",
    default="./config.json",
)
@click.pass_context
def main(ctx: click.Context, config_path: Path):
    # Send help if no subcommand
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

    else:
        try:
            ctx.obj = Config.load(config_path)
        except ValidationError as e:
            logger.error("failed to load configuration")

            for err in e.errors():
                location = ".".join(err["loc"])
                styled = click.style(location, fg="yellow")

                message = err["msg"]

                click.echo(f"\t{styled}: {message}")

            exit(1)


@main.command(help="Check that the configuration is valid")
@click.pass_obj
def validate(cfg: Config):
    logger.info("Running tests..")
    for test in tests.METHODS:
        click.echo(test(cfg))
    logger.info("Done!")


@main.command(help="Send the sponsor emails")
@click.option(
    "-s",
    "--single",
    is_flag=True,
    help="Send an email to the first company in the list",
)
@click.option(
    "-d",
    "--dry-run",
    is_flag=True,
    help="Pull and format the message but don't send anything",
)
@click.option(
    "-o", "--overwrite", help="Overwrite the recipient email for testing", default=None
)
@click.pass_obj
def send(cfg: Config, single: bool, dry_run: bool, overwrite: Optional[str]):
    if dry_run:
        Path("../dry-run-out").mkdir(exist_ok=True)

    logger.info(f"Settings: single={single} dry_run={dry_run} overwrite={overwrite}")

    try:
        success, skipped, total = sender.run(cfg, single, dry_run, overwrite)
        click.secho("Successfully sent ", fg="green", nl=False)
        click.secho(f"{success}/{total}", fg="blue", nl=False)
        click.secho(" sponsor emails!", fg="green", nl=False)
        if skipped != 0:
            click.secho(f" (Skipped {skipped} emails)", fg="yellow")
    except sender.SendException as e:
        logger.error(e.message)
        exit(1)


if __name__ == "__main__":
    main()
