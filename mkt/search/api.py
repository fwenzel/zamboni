from tastypie.authentication import Authentication
from tastypie.authorization import ReadOnlyAuthorization

import amo
from amo.helpers import absolutify

import mkt
from mkt.api.resources import AppResource
from mkt.search.views import _get_query, _filter_search
from mkt.search.forms import ApiSearchForm


class SearchResource(AppResource):

    class Meta(AppResource.Meta):
        resource_name = 'search'
        allowed_methods = []
        detail_allowed_methods = []
        list_allowed_methods = ['get']
        authorization = ReadOnlyAuthorization()
        authentication = Authentication()

    def get_resource_uri(self, bundle):
        # At this time we don't have an API to the Webapp details.
        return None

    def get_list(self, request=None, **kwargs):
        form = ApiSearchForm(request.GET if request else None)
        if not form.is_valid():
            raise self.form_errors(form)

        # Search specific processing of the results.
        region = getattr(request, 'REGION', mkt.regions.WORLDWIDE)
        qs = _get_query(region, gaia=request.GAIA,
                        mobile=request.MOBILE, tablet=request.TABLET)
        qs = _filter_search(qs, form.cleaned_data, region=region)
        res = amo.utils.paginate(request, qs)

        # Rehydrate the results as per tastypie.
        bundles = [self.build_bundle(obj=obj, request=request)
                   for obj in res.object_list]
        objs = [self.full_dehydrate(bundle) for bundle in bundles]
        # This isn't as quite a full as a full TastyPie meta object,
        # but at least it's namespaced that way and ready to expand.
        return self.create_response(request, {'objects': objs, 'meta': {}})

    def dehydrate_slug(self, bundle):
        return bundle.obj.app_slug

    def dehydrate(self, bundle):
        bundle = super(SearchResource, self).dehydrate(bundle)
        for size in amo.ADDON_ICON_SIZES:
            bundle.data['icon_url_%s' % size] = bundle.obj.get_icon_url(size)
        bundle.data['absolute_url'] = absolutify(bundle.obj.get_detail_url())
        return bundle
