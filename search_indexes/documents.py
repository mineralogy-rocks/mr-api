from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl.registries import registry
from django_elasticsearch_dsl_drf.compat import KeywordField, StringField
from elasticsearch_dsl import analyzer, tokenizer, Nested
import uuid
from django.db.models import Prefetch

from api.models import *

folding_analyzer = analyzer('folding_analyzer',
                            tokenizer=tokenizer('trigram', 'ngram', min_gram=3, max_gram=3),
                            filter=['lowercase', 'asciifolding']
                        )

# html_strip = analyzer(
#     'html_strip',
#     tokenizer="standard",
#     filter=["standard", "lowercase", "stop", "snowball"],
#     char_filter=["html_strip"]
# )

@registry.register_document
class MineralListDocument(Document):
    mineral_id = StringField(attr='mineral_id')
    mineral_name = StringField(analyzer=folding_analyzer)
    # mineral_name = KeywordField(fields={
    #         'raw': StringField(analyzer=folding_analyzer),
    #         'suggest': fields.CompletionField(multi=True),
    #     })
    formula = StringField(attr='mineral_formula_html')
    ns_index = StringField(attr='get_ns_index')
    status = fields.NestedField(attr='status',
           properties={
                   'status_id': KeywordField(
                       fields={
                            'raw': StringField(analyzer='keyword'),
                        }
                   ),
                   'description_short': KeywordField()
                   }
    )

    def get_indexing_queryset(self):
        return self.get_queryset()

    def get_queryset(self):
        queryset = super(MineralListDocument, self).get_queryset()
        queryset = queryset.select_related('id_class', 'id_subclass', 'id_family')
        queryset = queryset.prefetch_related('status')
        # queryset = queryset.prefetch_related(Prefetch('status', queryset=MsSpeciesStatus.objects.select_related('mineral_id','status_id')))
        return queryset

    class Index:
        # Name of the Elasticsearch index
        name = 'mineral_list'
        # See Elasticsearch Indices API reference for available settings
        settings = {
                'number_of_shards': 1,
                'number_of_replicas': 0,
                "max_ngram_diff": 50,
                "analysis": {
                    "analyzer": {
                        "standard_asciifolding": {
                        "tokenizer": "my_ngram_tokenizer",
                        "filter": ['lowercase', 'asciifolding', 'myngram']
                        }
                    },
                "filter": {
                        "myngram": {
                            "type": "ngram",
                            "min_gram": 3,
                            "max_gram": 3
                        }
                    },
                "tokenizer": {
                    "my_ngram_tokenizer": {
                        "type": "ngram",
                        "min_gram": 3,
                        "max_gram": 3
                    }
                }
            }
        }

    class Django:
        # The model associated with Elasticsearch document
        model = MineralList
        # related_models = (MsSpeciesStatus,)
        # fields = ('get_ns_index',)
        # The fields of the model you want to be indexed
        # in Elasticsearch
        # fields = ('mineral_name',)

        # Ignore auto updating of Elasticsearch when a model is saved
        # or deleted:
        # ignore_signals = True

        # Don't perform an index refresh after every update (overrides global setting):
        # auto_refresh = False

        # Paginate the django queryset used to populate the index with the specified size
        # (by default it uses the database driver's default setting)
        # queryset_pagination = 5000


# INDEX = Index('msspecies')

# # See Elasticsearch Indices API reference for available settings
# INDEX.settings(
#     number_of_shards=1,
#     number_of_replicas=1
# )

# folding_analyzer = analyzer('folding_analyzer',
#                             tokenizer=tokenizer('trigram', 'ngram', min_gram=3, max_gram=3),
#                             filter=['lowercase', 'asciifolding']
#                         )

# @INDEX.doc_type
# class MsSpeciesDocument(Document):
#     """MsSpecies Elasticsearch document."""
#     mineral_name = StringField(analyzer=folding_analyzer)

#     class Django(object):
#         """Inner nested class Django."""

#         model = MsSpecies  # The model associate with this Document