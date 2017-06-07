import logging
import six

# from sevenbridges.errors import ResourceNotModified
from sevenbridges.meta.resource import Resource
# from sevenbridges.decorators import inplace_reload
from sevenbridges.meta.fields import (HrefField, StringField)
from sevenbridges.meta.collection import Collection
from sevenbridges.http.advance_access import advance_access
from sevenbridges.models.link import Link
from sevenbridges.models.member import Member

logger = logging.getLogger(__name__)


class Datasets(Resource):
    """docstring for Datasets"""
    _URL = {
        'query': '/datasets',
        'members': '/datasets/{id}/members'
    }

    href = HrefField()
    id = StringField(read_only=True)
    name = StringField(read_only=False)

    def __str__(self):
        return six.text_type('<Datasets: id={id}>'.format(id=self.id))

    @classmethod
    def query(cls, api=None):
        api = api if api else cls._API
        with advance_access(api):
            return super(Datasets, cls)._query(
                url=cls._URL['query'], fields='_all',
                api=api
            )

    def members(self, id=None, api=None):
        response = self._api.get(
            url=self._URL['members'].format(id=self.id))
        data = response.json()
        total = response.headers['x-total-matching-query']
        members = [Member(api=self._api, **member) for member in data['items']]
        links = [Link(**link) for link in data['links']]
        href = data['href']
        return Collection(resource=Member, href=href, total=total,
                          items=members, links=links, api=self._api)
