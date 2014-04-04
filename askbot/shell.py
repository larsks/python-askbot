#!/usr/bin/env python

import os
import sys
import requests
import argparse
import itertools
import time
import yaml
from collections import namedtuple
import prettytable
import re
import jinja2

import askbot
from unicodecsv import UnicodeWriter

re_url = re.compile('(https?://.*/question/\d+/).*')

def format_date(d):
    return time.strftime('%Y-%m-%d', time.gmtime(int(d)))

def format_tags(t):
    return ' '.join(t)

def format_url(u):
    if args.short_urls:
        mo = re_url.match(u)
        if mo:
            return mo.group(1)

    return u

Column = namedtuple('column', ['label', 'align', 'max_width', 'attribute',
                               'formatter', 'default'])

columns = [
    Column('ID', None, None, 'id', None, True), 
    Column('Author', None, 15, lambda q: q['author']['username'], None, True), 
    Column('Posted', None, None, 'added_at', format_date, True), 
    Column('Latest', None, None, 'last_activity_at', format_date, True), 
    Column('Tags', 'l', None, 'tags', format_tags, True), 
    Column('Answers', None, None, 'answer_count', None, True), 
    Column('Score', None, None, 'score', None, False), 
    Column('Title', 'l', 40, 'title', None, True), 
    Column('URL', 'l', None, 'url', format_url, False), 
]

Row = namedtuple('row', [c.label for c in columns])

default_config_file = os.path.join(
    os.environ['HOME'], '.config', 'askbot.yml')

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--short-urls', '-u', action='store_true')
    p.add_argument('--pretty', '-P',
                   action='store_const',
                   const='pretty',
                   dest='format',
                   help='Generate pretty-printed output')
    p.add_argument('--csv', '-C',
                   action='store_const',
                   const='csv',
                   dest='format',
                   help='Generate CSV output')
    p.add_argument('--answered',
                   action='store_const',
                   const='answered',
                   dest='scope',
                   help='An alias for --scope answered')
    p.add_argument('--unanswered',
                   action='store_const',
                   const='unanswered',
                   dest='scope',
                   help='An alias for --scope unanswered')
    p.add_argument('--tag', '-t',
                   action='append',
                   default=[],
                   help=('Select messages with this tag '
                         '(may be specified multiple times)'))
    p.add_argument('--endpoint', '-E',
                   help='AskBot API endpoint')
    p.add_argument('--query', '-q',
                   help='An arbitrary text query to apply to searches')
    p.add_argument('--sort', '-s',
                   default='age-desc',
                   choices=askbot.sort_choices,
                   help='Select sort key and order')
    p.add_argument('--scope', '-S',
                   default='all',
                   choices=askbot.scope_choices)
    p.add_argument('--author', '-a',
                   type=int,
                   help='Select questions by this author (numeric id)')
    p.add_argument('--limit', '-l',
                   type=int,
                   help='Limit number of results')
    p.add_argument('--config', '-f',
                   default=default_config_file,
                   help='Path to configuration file')
    p.add_argument('--column', '-c',
                   action='append',
                   help='Select columns to output in --pretty mode')
    p.add_argument('--template', '-T',
                   help='Render output using the provided jinja2 template')

    p.set_defaults(format='pretty')

    return p.parse_args()

def output_csv(rows):
    global args

    writer = UnicodeWriter(sys.stdout)
    writer.writerows(rows)

def output_pretty(rows):
    global args

    t = prettytable.PrettyTable([c[0] for c in columns])
    t.hrules = prettytable.ALL

    for c in columns:
        if c.align is not None:
            t.align[c.label] = c.align

        if c.max_width is not None:
            t.max_width[c.label] = c.max_width

    for row in rows:
        t.add_row(row)

    print t.get_string(fields=args.column)

def output_template(rows):
    global args

    with open(args.template) as fd:
        t = jinja2.Template(fd.read())

    print t.render(rows=rows)

def main():
    global args
    args = parse_args()

    try:
        with open(args.config) as fd:
            cfg = yaml.load(fd)
            cfg = cfg.get('askbot') if cfg else {}
    except IOError:
        cfg = {}

    if args.endpoint is None:
        args.endpoint = cfg.get('endpoint')

    if args.limit is None:
        args.limit = cfg.get('limit')

    if args.column is None:
        args.column = [c.label for c in columns if c.default]

    bot = askbot.Askbot(endpoint=args.endpoint)
    rows = []
    for q in bot.questions(author=args.author, sort=args.sort,
                           scope=args.scope, query=args.query,
                           tags=args.tag, limit=args.limit):
        row = []
        for c in columns:
            val = (c.attribute(q) if callable(c.attribute)
                   else q[c.attribute])

            if callable(c.formatter):
                val = unicode(c.formatter(val))
            else:
                val = unicode(val)

            row.append(val)

        rows.append(Row(*row))

    if args.template:
        output_template(rows)
    elif args.format == 'csv':
        output_csv(rows)
    elif args.format == 'pretty':
        output_pretty(rows)

if __name__ == '__main__':
    sys.exit(main())

