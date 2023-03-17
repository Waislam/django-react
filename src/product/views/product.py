from django.views import generic
from django.views.generic import ListView
from datetime import date
from product.models import Variant, Product, ProductVariant, ProductVariantPrice
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context


class ListProductView(generic.TemplateView):
    template_name = 'products/list.html'

    def get_context_data(self, **kwargs):
        context = super(ListProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        productVariants = ProductVariant.objects.all()
        product_variant_price = ProductVariantPrice.objects.all()
        vari = self.request.GET.get('variant')
        title = self.request.GET.get('title')
        created_at = self.request.GET.get('date')
        price_from = self.request.GET.get('price_from')
        price_to = self.request.GET.get('price_to')

        if title:
            product_all = Product.objects.filter(title=title)
        elif created_at:
            make_list = str(created_at).split('-')
            year = int(make_list[0])
            month = int(make_list[1])
            day = int(make_list[2])
            product_all = Product.objects.filter(created_at__contains=date(year, month, day))
        elif price_from and price_to:
            product_all = Product.objects.filter(productvariantprice__price__range=(price_from, price_to))
        elif vari != None:
            product_all = Product.objects.filter(productvariant__variant_title=vari)
        else:
            product_all = Product.objects.all()
        # context['products'] = product_all
        context['variants'] = list(variants.all())
        new_set = set()
        # for i in productVariants:
        #     new_set.add(i)

        list_of_dict = []
        for variant in variants:
            title = variant['title']
            title_list = list()
            new_dict = {}
            new_dict['title'] = title
            for pvariant in productVariants.filter(variant=variant['id']):
                title_list.append(pvariant.variant_title)

            make_unique = set(title_list)
            make_again_list = list(make_unique)
            # add list to dict
            new_dict['sub_title'] = make_again_list
            # now add dict to the list
            list_of_dict.append(new_dict)

        # context['productVariants'] = new_set
        context['productVariantPrice'] = product_variant_price
        context['variants_title_sub_title'] = list_of_dict

        # pagination handle
        page_number = self.request.GET.get('page')
        paginator = Paginator(product_all, 2)
        try:
            current_page_data = paginator.page(page_number)
        except PageNotAnInteger:
            current_page_data = paginator.page(1)
        total_pages =  paginator.num_pages
        total_page_list = [page+1 for page in range(total_pages)]

        context['page_start_index'] = current_page_data.start_index()
        context['page_end_index'] = current_page_data.end_index()

        context['page'] = page_number
        context['totalproduct'] = paginator.count
        context['products'] = current_page_data
        context['page_list'] = total_page_list


        return context
