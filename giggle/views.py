from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from .apis import get_giggle_result
from .models import Joke


def giggle_search(request):
    context = {}
    if request.method == 'POST':
        query = request.POST.get('query')

        # 1. Input Validation
        if not query or len(query.strip()) == 0 or len(query) > 50:
            messages.error(request, 'Query must be between 1 and 50 characters.')
            return redirect('giggle_search')

        # 2. Check Database First (Cache Layer)
        existing_joke = Joke.objects.filter(query__iexact=query).first()

        if existing_joke:
            context['query'] = existing_joke.query
            context['response'] = existing_joke.response
            messages.success(request, 'Joke retrieved from history!')
        else:
            # 3. Call API if not in DB
            response = get_giggle_result(query)

            if response == 1:
                messages.error(request, 'Rate limit reached or API error. Try again later.')
            else:
                context['query'] = query.capitalize()
                context['response'] = response
                # Save new joke
                Joke.objects.create(query=query, response=response)

    return render(request, './giggle/giggle_search.html', context)

def giggle_history(request):
    jokes = Joke.objects.all().order_by("-created_at")
    paginator = Paginator(jokes, 8)
    page_no = request.GET.get('page',1)
    curr_page = paginator.get_page(page_no)
    return render(request, './giggle/giggle_history.html', context={'jokes': curr_page})

def delete_joke(request, pk):
    joke_to_delete = get_object_or_404(Joke, pk=pk)
    joke_to_delete.delete()
    return redirect('giggle_history')