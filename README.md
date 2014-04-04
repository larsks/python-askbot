This is a Python module for interacting with the [AskBot][] [remote
api][].

[askbot]: http://askbot.org/
[remote api]: http://askbot.org/doc/api.html

This module includes a command line tool for performing askbot
queries.

Synopsis
========

    usage: askbot [-h] [--short-urls] [--pretty] [--csv] [--answered]
                  [--unanswered] [--tag TAG] [--endpoint ENDPOINT] [--query QUERY]
                  [--sort {age-asc,age-desc,activity-asc,activity-desc,answers-asc,answers-desc,votes-asc,votes-desc,relevance-asc,relevance-desc}]
                  [--scope {all,unanswered}] [--author AUTHOR] [--limit LIMIT]
                  [--config CONFIG] [--column COLUMN] [--template TEMPLATE]

    optional arguments:
      -h, --help            show this help message and exit
      --short-urls, -u
      --pretty, -P          Generate pretty-printed output
      --csv, -C             Generate CSV output
      --answered            An alias for --scope answered
      --unanswered          An alias for --scope unanswered
      --tag TAG, -t TAG     Select messages with this tag (may be specified
                            multiple times)
      --endpoint ENDPOINT, -E ENDPOINT
                            AskBot API endpoint
      --query QUERY, -q QUERY
                            An arbitrary text query to apply to searches
      --sort {age-asc,age-desc,activity-asc,activity-desc,answers-asc,answers-desc,votes-asc,votes-desc,relevance-asc,relevance-desc}, -s {age-asc,age-desc,activity-asc,activity-desc,answers-asc,answers-desc,votes-asc,votes-desc,relevance-asc,relevance-desc}
                            Select sort key and order
      --scope {all,unanswered}, -S {all,unanswered}
      --author AUTHOR, -a AUTHOR
                            Select questions by this author (numeric id)
      --limit LIMIT, -l LIMIT
                            Limit number of results
      --config CONFIG, -f CONFIG
                            Path to configuration file
      --column COLUMN, -c COLUMN
                            Select columns to output in --pretty mode
      --template TEMPLATE, -T TEMPLATE
                            Render output using the provided jinja2 template

Configuration
=============

The `askbot` script will read configuration from a YAML format
configuration file, by default `~/.config/askbot.yml`.  You can
specify an alternative with the `--config` command line option.

The configuration must be a mapping inside a top-level `askbot`
element.  For example:

    askbot:
      endpoint: https://ask.openstack.org/en/api/v1
      limit: 100

This sets an endpoint appropriate for use with
http://ask.openstack.org/ and limits the number of results to 100 by
default.

Examples
========

> These examples assume you are using the `ask.openstack.org` endpoint.

Show me the 5 most recent unanswered questions tagged `rdo`, displaying only the question id, author, and title:

    $ askbot -l 5 -t do -c Question -c Author -c Title
    +----------+---------------+------------------------------------------+
    | Question |     Author    | Title                                    |
    +----------+---------------+------------------------------------------+
    |  26431   |     visanj    | Would like to learn Openstack, is RDO    |
    |          |               | useful?                                  |
    +----------+---------------+------------------------------------------+
    |  26264   |    53dville   | trying to install RDO on centos 6.5,     |
    |          |               | fails installing dashboard components    |
    +----------+---------------+------------------------------------------+
    |  26193   |     Romain    | RDO neutron on github                    |
    +----------+---------------+------------------------------------------+
    |  26143   |  Diogo Vieira | Why doesn't my instance recognise more   |
    |          |               | space in the disk after a cinder         |
    |          |               | expansion?                               |
    +----------+---------------+------------------------------------------+
    |  26142   |  Diogo Vieira | Why doesn't my instance doesn't          |
    |          |               | recognise more space on disk?            |
    +----------+---------------+------------------------------------------+
    |  26049   |  pawankkamboj | Packstack install error during neutron   |
    |          |               | setup                                    |
    +----------+---------------+------------------------------------------+
    |  25995   |  vaidyanath-m | Inspite of successfull installation      |
    |          |               | unable to open horizon                   |
    +----------+---------------+------------------------------------------+
    |  25960   | rkrishnan2012 | Can't access vm's externally             |
    +----------+---------------+------------------------------------------+
    |  25949   |      dubi     | Neutron allinone external net problem    |
    |          |               | after reboot                             |
    +----------+---------------+------------------------------------------+
    |  25947   |    ccowley    | Openstack Neutron stability problems     |
    |          |               | with OpenVSwitch                         |
    +----------+---------------+------------------------------------------+

Show me the URLs for the five questions tagged RDO with the most answers:

    $ askbot -t rdo --sort answers-desc -l 5 --csv | cut -d, -f8
    https://ask.openstack.org/en/question/8540/rdo-neutron-multinode-single-nic/
    https://ask.openstack.org/en/question/8946/external-gateway/
    https://ask.openstack.org/en/question/12439/metadata-agent-throwing-attributeerror-httpclient-object-has-no-attribute-auth_tenant_id-with-latest-release/
    https://ask.openstack.org/en/question/25295/openstack-dnsaas-options-for-havana/
    https://ask.openstack.org/en/question/25917/how-to-upgrade-keystone/

Using Templates
===============

The `--template` option allows you to produce output by rendering a
[Jinja2][] template.  For example, the following template:

    {% for row in rows %}
    {{'%6s' % row.ID}}: {{row.Title}}
            Posted: {{row.Posted}} Last activity: {{row.Latest}}
            {{row.URL}}
    {% endfor %}

Might produce output like this:

     25926: Invalid nova.conf file with RDO installation
            Posted: 2014-03-27 Last activity: 2014-03-27
            https://ask.openstack.org/en/question/25926/

     25837: Supply extra arguments to kvm parameters
            Posted: 2014-03-25 Last activity: 2014-03-25
            https://ask.openstack.org/en/question/25837/

[jinja2]: http://jinja.pocoo.org/docs/

