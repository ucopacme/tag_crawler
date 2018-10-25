#!/usr/bin/env python
'''
TagFilters=[
    {
        'Key': 'string',
        'Values': [
            'string',
        ]
    },
],
ResourceTypeFilters=[
    'string',
]

./tag_crawler.py -r awsauth/OrgAdmin| tee /tmp/all_tag_keys.yaml
/tmp> egrep -v "Account|TagKeys|Regions|us-*-*" all_tag_keys.yaml | sort -u > all_tag_keys.sort-u.txt


'''

import click
import boto3
from organizer import crawlers, orgs, utils


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--role', '-r',
    required=True,
    help='IAM role for accessing AWS Organization accounts',
)
@click.option('--resource-filter', '-rf', 'resource_filter',
    multiple=True,
    help='AWS resource name to filter by. Can be used multiple times.',
)
@click.option('--tag-filter', '-tf', 'tag_filter',
    multiple=True,
    help='Tag to filter by. Can be used multiple times. Must be a string. '
    'Can be either a key name or a key/value pair saparated by a comma. '
    'Tags containing spaces must be quoted.',
)
@click.option('--show-resource-only',
    is_flag=True,
    help='Display only the ARN of matching resources.',
)
@click.option('--show-keys-only',
    is_flag=True,
    help='Display only tag key names.',
)
def cli(role, tag_filter, resource_filter, show_resource_only, show_keys_only):
    #click.echo(tag_filter)
    #click.echo(resource_filter)
    filters = parse_filters(tag_filter, resource_filter)
    #click.echo(utils.yamlfmt(filters))
    crawler = get_crawler(role)
    if show_keys_only:
        execution = crawler.execute(get_tag_keys)
    else:
        execution = crawler.execute(get_tagged_resources, filters, show_resource_only)
    output = output_regions_per_account(execution)
    click.echo(utils.yamlfmt(output))


def parse_filters(tag_filter, resource_filter):
    filters = dict()
    if tag_filter is not None:
        filters['TagFilters'] = munge_tag_filter(tag_filter)
    if resource_filter is not None:
        filters['ResourceTypeFilters'] = list(resource_filter)
    return filters


def munge_tag_filter(tag_filter):
    _filter = []
    for tag in tag_filter:
        key, sep, value = tag.partition(',')
        if value:
            _filter.append(dict(Key=key, Values=[value]))
        else:
            _filter.append(dict(Key=key))
    return _filter


def get_crawler(org_access_role):
    master_account_id = utils.get_master_account_id(org_access_role)
    my_org = orgs.Org(master_account_id, org_access_role)
    my_org.load()
    my_crawler = crawlers.Crawler(
        my_org,
        access_role=org_access_role,
        accounts=['ait-poc', 'ashley-training', 'ucop-its'],
        regions=['us-west-2', 'us-east-1'],
    )
    my_crawler.load_account_credentials()
    return my_crawler


def get_tag_keys(region, account):
    """
    Crawler payload function
    """
    client = boto3.client(
        'resourcegroupstaggingapi',
        region_name=region,
        **account.credentials
    )
    response = client.get_tag_keys()
    tag_key_list = response['TagKeys']
    while response['PaginationToken']:
        response = client.get_tag_keys(
            PaginationToken=response['PaginationToken'],
        )
        tag_key_list += response['TagKeys']
    return dict(TagKeys=tag_key_list)


def get_tagged_resources(region, account, filters, show_resource_only):
    """
    Crawler payload function
    """
    client = boto3.client(
        'resourcegroupstaggingapi',
        region_name=region,
        **account.credentials,
    )
    response = client.get_resources(
        **filters,
    )
    tag_mapping_list = munge_tag_map(response, show_resource_only)
    while response['PaginationToken']:
        response = client.get_resources(
            **filters,
            PaginationToken=response['PaginationToken'],
        )
        tag_mapping_list += munge_tag_map(response, show_resource_only)
    label = 'ResourceARN' if show_resource_only else 'ResourceTagMappingList'
    return {label: tag_mapping_list}


def munge_tag_map(response, show_resource_only):
    if show_resource_only:
        return [tag_map['ResourceARN'] for tag_map in response['ResourceTagMappingList']]
    else:
        return response['ResourceTagMappingList']


def output_regions_per_account(execution):
    """ generate dictionary of responses per account """
    collector = []
    responses = purge_empty_responses(execution)
    account_names = sorted(list(set([r.account.name for r in responses])))
    for account_name in account_names:
        d = dict(
            Account=account_name,
            Regions=[{r.region: r.payload_output}
                for r in responses
                if r.account.name == account_name
            ]
        )
        collector.append(d)
    return(collector)


def purge_empty_responses(execution):
    '''
    Return list of execution responses for which output is not empty.
    Expects each response to be a list of dict.
    '''
    responses = [
        r for r in execution.responses 
        if len(r.payload_output) == 1
        and list() not in r.payload_output.values()
    ]
    return responses


if __name__ == "__main__":
    cli()
