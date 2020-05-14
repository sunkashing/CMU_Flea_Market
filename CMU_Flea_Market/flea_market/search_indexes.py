from haystack import indexes
from flea_market.models import Item


class ItemIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Item

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
