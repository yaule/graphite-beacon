import copy


class ElasticsearchRecord(object):
    def __init__(self, query, fields, metric, mfield, gte, lte):
        self.query = query
        self.fields = fields
        self.metric = metric
        self.mfield = mfield
        self.gte = gte
        self.lte = lte

    def body(self):
        self.body = {
            "query": {
            "bool": {
                "must": [
                {
                    "range": {
                    "@timestamp": {
                        "gte": self.gte,
                        "lte": self.lte,
                        "format": "epoch_millis"
                    }
                    }
                }
                ],
                "must_not": []
            }
            },
            "aggs": {}
        }

        if self.query:
            search = {
              "query_string": {
                "query": self.query,
                "analyze_wildcard": True
              }
            }
        else:
            search = {
              "match_all": {}
            }

        self.body['query']['bool']['must'].append(search)

        if self.fields:
            self.body.update(self._aggs())

        return self.body

    def _aggs(self):
        d = dict()
        for field in reversed(self.fields):
            aggs_dict = {
              "aggs":{
                field: {
                  "terms": {
                    "field": field
                  },
                  "aggs": d.get('aggs', {})
                }
              }
            }

            if self.metric != 'count':
                metric_dict = {
                  self.metric: {
                    self.metric: {
                      "field": self.mfield
                    }
                  }
                }
                aggs_dict['aggs'][field]['aggs'].update(metric_dict)
            d = aggs_dict
        return aggs_dict

    def parse(self, data):
        res = []
        if not self.fields:
            v = data['hits']['total']
            res.append([v])
            return res

        field_map = {}
        for i, field in enumerate(self.fields):
            field_map[field] = i
        f = [None] * (len(self.fields)+1)
        data = data['aggregations']
        def scan_data(d):
            control = 0
            flag = False
            for field in self.fields:
                control += 1
                if field in d:
                    value = d[field]
                    for bucket in value["buckets"]:
                        if "key_as_string" in bucket:
                            f[field_map[field]] = bucket['key_as_string']
                        elif "key" in bucket:
                            f[field_map[field]] = bucket['key']
                        scan_data(bucket)
                        if control == len(self.fields):
                            if self.metric == 'count':
                                v = bucket['doc_count']
                            else:
                                v = bucket[self.metric]['value']
                            f[-1] = v
                            res.append(copy.copy(f))
        scan_data(data)
        return res
