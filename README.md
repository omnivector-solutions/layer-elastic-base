# Layer-Elastic-Base

This layer exists to aid in making the installation of 
elastic.co software more consistent among the elastic.co charms.

# Usage
To use this layer, simply include it in your layer's layer.yaml,
and define the `elastic-pkg` as a layer option for layer elastic-base.

Example `mycharm/layer.yaml`
```yaml
include:
  - 'layer:basic'
  - 'layer:elastic-base'
options:
  elastic-base:
    elastic-pkg: "logstash"
```

Example `mycharm/reactive/mycharm.py`
```python
@when_any('apt.installed.logstash',
          'deb.installed.logstash')
@when_not('logstash.elasticsearch.configured')
def get_all_elasticsearch_nodes_or_all_master_nodes():
    cache = kv()
    if cache.get('logstash.elasticsearch', ''):
        hosts = cache.get('logstash.elasticsearch')
    else:
        hosts = []
    ...
    ...
```

# Elastic DEB Resources
To deploy your own .deb of any elastic.co software, simply download the deb and 
attach it as a resource when deploying your built elastic.co software charm.


### Copyright
* AGPLv3 (see `copyright` file in this directory)

### Contact Information

* James Beedy <jamesbeedy@gmail.com>
