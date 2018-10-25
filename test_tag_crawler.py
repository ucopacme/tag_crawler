import tag_crawler


def test_munge_tag_filter():
    tag_filter0 = ('Name',)
    result0 = tag_crawler.munge_tag_filter(tag_filter0)
    print(result0)
    assert isinstance(result0, list)
    assert len(result0) == 1
    assert 'Key' in result0[0] 
    assert result0[0]['Key'] == 'Name'

    tag_filter1 = ('Name', 'Application')
    result1 = tag_crawler.munge_tag_filter(tag_filter1)
    print(result1)
    assert len(result1) == 2
    for f in tag_filter1:
        assert dict(Key=f) in result1

    tag_filter2 = ('Name,snoopy', 'Application,lucy')
    result2 = tag_crawler.munge_tag_filter(tag_filter2)
    print(result2)
    for f in result2:
        assert 'Key' in f
        assert 'Values' in f
        assert isinstance(f['Values'], list)
        assert len(f['Values']) == 1
    assert result2[0]['Values'][0] == 'snoopy'
    assert result2[1]['Values'][0] == 'lucy'
    #assert False


def test_parse_filters():
    tag_filter = ('Name,snoopy', 'Application,lucy')
    resource_filter = ('ec2:instance', 'ec2:vpc')
    filters = tag_crawler.parse_filters(tag_filter, resource_filter)
    print(filters)
    assert isinstance(filters, dict)
    assert 'TagFilters' in filters
    assert filters['TagFilters'] == tag_crawler.munge_tag_filter(tag_filter)

    assert 'ResourceTypeFilters' in filters
    assert isinstance(filters['ResourceTypeFilters'], list) 
    assert len(filters['ResourceTypeFilters']) == 2
    for f in resource_filter:
        assert f in filters['ResourceTypeFilters']
    #assert False

