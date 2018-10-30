tag_crawler
===========

A tool for manipulating AWS resource tags across multiple accounts within an organization.  

Installation
------------

::

  pip install https://github.com/ucopacme/tag_crawler/archive/master.zip


Usage
------

::

  (python3.6) agould@horus:~> tag_crawler -h
  Usage: tag_crawler [OPTIONS]
  
  Options:
    -r, --role TEXT              IAM role for accessing AWS Organization
                                 accounts  [required]
    -rf, --resource-filter TEXT  AWS resource name to filter by. Can be used
                                 multiple times.
    -tf, --tag-filter TEXT       Tag to filter by. Can be used multiple times.
                                 Must be a string. Can be either a key name or a
                                 key/value pair saparated by a comma. Tags
                                 containing spaces must be quoted.
    --show-resource-only         Display only the ARN of matching resources.
    --show-keys-only             Display only tag key names.
    -h, --help                   Show this message and exit.


collect all taggable resources and thier tags for all accounts and regions::

  (python3.6) agould@horus:~> tag_crawler -r awsauth/OrgAdmin

collect just taggable resource arn::

  (python3.6) agould@horus:~> tag_crawler -r awsauth/OrgAdmin --show-resource-only

just tag keys only::

  (python3.6) agould@horus:~> tag_crawler -r awsauth/OrgAdmin --show-keys-only

filter by resource name::

  (python3.6) agould@horus:~> tag_crawler -r awsauth/OrgAdmin --resource-filter ec2:instance

filter by tag::

(python3.6) agould@horus:~> tag_crawler -r awsauth/OrgAdmin --tag-filter env,prod

multiple filters are `ANDed`::

(python3.6) agould@horus:~> tag_crawler -r awsauth/OrgAdmin -rf ec2 -tf env,poc -tf aws:cloudformation:stack-id






Optional
--------

for bash tab completion add this to your ~/.bashrc::

  # tag_crawler tab completion
  eval "$(_TAG_CRAWLER_COMPLETE=source tag_crawler)"

this does not work in virtual environemnts.  needs work...
