import csv
import datetime as dt
import io

import click

import exchrate


@click.command()
@click.argument('date_from', type=click.DateTime())
@click.argument('date_to', type=click.DateTime())
def cli(date_from: dt.datetime, date_to: dt.datetime):
    e = exchrate.ExchangeRateParse(
        'NBU-json',
        (date_from.date().isoformat(), date_to.date().isoformat()),
        'USD',
        'UAH',
    )
    rates = e.get_exch_rate()
    out = io.StringIO()
    writer = csv.writer(out)
    rows = [['date', 'rate']]
    rows.extend([[row.exdate, row.exrate] for row in rates])
    writer.writerows(rows)
    click.echo(out.getvalue())


if __name__ == '__main__':
    cli()
