from django.shortcuts import render, redirect
from .models import Work, AddWorkForm
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse("Error Rendering PDF", status=400)

# from easy_pdf.views import PDFTemplateView
# import easy_pdf
# from easy_pdf.rendering import render_to_pdf_response
# class PDFView(PDFTemplateView):
#     template_name = 'pdf/invoice_generator.html'
#     download_filename = 'hello.pdf'

#     def get_context_data(self, **kwargs):
#         return self.request.GET

def generate_pdf(request):
    context = request.GET
    request.session['context'] = context
    return redirect('get_pdf')

def get_pdf(request):
    pdf = render_to_pdf('pdf/invoice_generator.html', request.session['context'])
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Invoice_%s.pdf" %("12341231")
        content = "inline; filename='%s'" %(filename)
        content = "attachment; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")

def homepage(request):
    return render(request, 'base.html')

def invoice_generator(request):
    works = Work.objects.all().order_by('code')
    return render(request, 'invoice.html', {'works': works})

def get_code_values(request):
    if request.method == 'GET':
        code = request.GET.get('code')
        work = Work.objects.get(code=code)
        data = {
            'id': work.id,
            'code': work.code,
            'name': work.name,
            'amount': work.amount
        }
        return JsonResponse(data)

def admin(request):
    '''
        To add new work entry.
        User can add a new entry with Work Code, Work Name and Work Rate/Amount
    '''
    form = AddWorkForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'New Entry Added successfully')
        form = AddWorkForm()
    works = Work.objects.all().order_by('-date_added')
    return render(request, 'admin.html', {'form': form, 'works': works})

def admin_edit(request, id):
    '''
        To edit a single work entry that is already created
    '''
    work = get_object_or_404(Work, id=id)
    if request.method == 'POST':
        form = AddWorkForm(request.POST, instance=work)
        if form.is_valid():
            form.save()
        messages.success(request, 'Entry Edited successfully')
        return redirect('admin')
    else:
        form = AddWorkForm(initial={
                                'code'  : work.code,
                                'name'  : work.name,
                                'amount': work.amount 
                            }, instance=work)
        return render(request, 'admin_edit_modal.html', {'form': form})

def admin_delete(request, id):
    '''
        To delete a single entry already created
    '''
    work = get_object_or_404(Work, id=id)
    work.delete()
    messages.success(request, 'Entry Deleted successfully')
    return redirect('admin')