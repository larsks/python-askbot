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
import cStringIO

import askbot
from unicodecsv import UnicodeWriter

column = namedtuple('column', ['label', 'align', 'max_width', 'attribute',
                               'formatter', 'default'])

def format_date(d):
    return time.strftime('%Y-%m-%d', time.gmtime(int(d)))

def format_tags(t):
    return ' '.join(t)

columns = [
    column('Question', None, None, 'id', None, True), 
    column('Author', None, 15, lambda q: q['author']['username'], None, True), 
    column('Posted', None, None, 'added_at', format_date, True), 
    column('Latest', None, None, 'last_activity_at', format_date, True), 
    column('Tags', 'l', None, 'tags', format_tags, True), 
    column('Answers', None, None, 'answer_count', None, True), 
    column('Title', 'l', 40, 'title', None, True), 
    column('URL', 'l', None, 'url', None, False), 
]

default_config_file = os.path.join(
    os.environ['HOME'], '.config', 'askbot.yml')

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--pretty', '-P',
                   action='store_const',
                   const='pretty',
                   dest='format')
    p.add_argument('--csv', '-C',
                   action='store_const',
                   const='csv',
                   dest='format')
    p.add_argument('--tag', '-t',
                   action='append',
                   default=[])
    p.add_argument('--unanswered', '-u')
    p.add_argument('--endpoint', '-E')
    p.add_argument('--query', '-q')
    p.add_argument('--sort', '-s',
                   default='age-desc',
                   choices=askbot.sort_choices)
    p.add_argument('--scope', '-S',
                   default='all',
                   choices=askbot.scope_choices)
    p.add_argument('--author', '-a',
                   type=int)
    p.add_argument('--limit', '-l',
                   type=int)
    p.add_argument('--config', '-f',
                   default=default_config_file)
    p.add_argument('--column', '-c',
                   action='append')

    p.set_defaults(format='pretty')

    return p.parse_args()

def output_csv(rows, args):
    writer = UnicodeWriter(sys.stdout)
    writer.writerows(rows)

def output_pretty(rows, args):
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

def main():
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

        rows.append(row)

    if args.format == 'csv':
        output_csv(rows, args)
    elif args.format == 'pretty':
        output_pretty(rows, args)

if __name__ == '__main__':
    sys.exit(main())

