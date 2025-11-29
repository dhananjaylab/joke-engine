from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from .apis import get_giggle_result
from .apis import generate_meme_image, heckle_evaluation, explain_joke_text
from .models import Joke


def giggle_search(request):
    context = {}
    # default style for rendering the form
    context['style'] = 'witty'
    if request.method == 'POST':
        # Handle quick heckle submission from home page
        heckle_input = request.POST.get('heckle_joke')
        if heckle_input is not None:
            heckle_input = heckle_input.strip()
            if not heckle_input:
                messages.error(request, 'Please enter a joke to be heckled.')
                return redirect('giggle_search')
            result = heckle_evaluation(heckle_input)
            context['heckle_input'] = heckle_input
            context['heckle_result'] = result
            return render(request, './giggle/giggle_search.html', context)

        query_text = request.POST.get('query')
        style = request.POST.get('style', 'witty')
        regenerate = request.POST.get('regenerate', None)

        # Input Validation
        if not query_text or len(query_text.strip()) == 0 or len(query_text) > 100:
            messages.error(request, 'Query must be between 1 and 100 characters.')
            return redirect('giggle_search')

        # Composite key to separate same topic but different styles
        composite_query = f"{query_text.strip()} [{style}]"

        # Check cache unless user explicitly asked to regenerate
        existing_joke = None if regenerate else Joke.objects.filter(query__iexact=composite_query).first()

        if existing_joke:
            context['query'] = existing_joke.query
            context['response'] = existing_joke.response
            # also expose original topic and style for template actions
            context['topic'] = query_text.strip()
            context['style'] = style
            context['joke_id'] = existing_joke.id
            messages.success(request, 'Joke retrieved from history!')
        else:
            # Call API
            response = get_giggle_result(query_text.strip(), style)

            if response == 1:
                messages.error(request, 'Rate limit reached or API error. Try again later.')
            else:
                context['query'] = composite_query
                context['response'] = response
                context['topic'] = query_text.strip()
                context['style'] = style
                # Save new joke (cache)
                new_joke = Joke.objects.create(query=composite_query, response=response)
                context['joke_id'] = new_joke.id

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


def heckle_station(request):
    """A playful view where users submit their own joke and the AI rates/roasts it."""
    context = {}
    if request.method == 'POST':
        user_joke = request.POST.get('user_joke', '').strip()
        if not user_joke:
            messages.error(request, 'Please enter a joke to be heckled.')
            return redirect('heckle_station')

        # Call the heckle evaluator
        result = heckle_evaluation(user_joke)
        context['user_joke'] = user_joke
        context['heckle'] = result

    return render(request, './giggle/heckle_station.html', context)


def explain_joke(request, pk):
    """Return an explanation for a joke. If called via AJAX/fetch, return JSON."""
    joke = get_object_or_404(Joke, pk=pk)
    explanation = explain_joke_text(joke.response)
    # Simple JSON response for fetch/HTMX
    from django.http import JsonResponse
    return JsonResponse({'explanation': explanation})


def generate_meme(request, pk):
    """Generate an image for the given joke and return the image URL as JSON."""
    joke = get_object_or_404(Joke, pk=pk)
    image_url = generate_meme_image(joke.response)
    from django.http import JsonResponse
    if image_url:
        return JsonResponse({'image_url': image_url})
    else:
        return JsonResponse({'error': 'Image generation failed'}, status=500)