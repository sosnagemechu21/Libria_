import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import Conversation, Message


PLACEHOLDER_RESPONSES = {
    'mathematics': "Let's think through this step by step. What specific concept are you working on — algebra, geometry, or calculus? I can help you break it down.",
    'physics': "Physics is about understanding the world through principles. Can you tell me which formula or concept is confusing you? Let's build intuition first.",
    'biology': "Great subject! Biology is best understood through systems. Are you studying cells, organisms, or ecosystems? Let's connect the ideas.",
    'chemistry': "Chemistry makes sense when you understand atoms and bonds. Which topic — periodic table, reactions, or stoichiometry?",
    'default': "I'm your Libria study companion 📚. Set up your AI key in Profile Settings to unlock full AI responses. For now: what concept would you like to explore?",
}


@login_required
def chat_home(request):
    conversations = Conversation.objects.filter(user=request.user).prefetch_related('messages')[:20]
    return render(request, 'ai_assistant/home.html', {'conversations': conversations})


@login_required
def new_conversation(request):
    textbook_id = request.GET.get('textbook')
    textbook = None
    if textbook_id:
        from library.models import Textbook
        textbook = get_object_or_404(Textbook, pk=textbook_id)
    conv = Conversation.objects.create(
        user=request.user,
        textbook=textbook,
        title=f"Study session - {textbook.subject.name if textbook else 'General'}",
    )
    return redirect('ai_assistant:chat', conv_id=conv.pk)


@login_required
def chat(request, conv_id):
    conversation = get_object_or_404(Conversation, pk=conv_id, user=request.user)
    messages_qs = conversation.messages.order_by('timestamp')
    return render(request, 'ai_assistant/chat.html', {
        'conversation': conversation,
        'messages': messages_qs,
    })


@login_required
def send_message(request, conv_id):
    """AJAX: receive user message, return AI response."""
    if request.method == 'POST':
        conversation = get_object_or_404(Conversation, pk=conv_id, user=request.user)
        data = json.loads(request.body)
        user_text = data.get('message', '').strip()
        if not user_text:
            return JsonResponse({'error': 'Empty message'}, status=400)

        Message.objects.create(
            conversation=conversation,
            role='user',
            content=user_text,
        )
        conversation.updated_at = timezone.now()

        # Check for real API key
        try:
            ai_key = request.user.profile.ai_api_key
            ai_provider = request.user.profile.ai_provider
        except Exception:
            ai_key = ''
            ai_provider = 'gemini'

        if ai_key:
            reply = _call_ai(ai_key, ai_provider, conversation, user_text)
        else:
            reply = _placeholder_reply(conversation, user_text)

        msg = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=reply,
        )
        conversation.save()
        return JsonResponse({
            'reply': reply,
            'timestamp': msg.timestamp.strftime('%H:%M'),
        })
    return JsonResponse({'error': 'invalid'}, status=400)


def _placeholder_reply(conversation, user_text):
    subject = ''
    if conversation.textbook:
        subject = conversation.textbook.subject.name.lower()
    key = next((k for k in PLACEHOLDER_RESPONSES if k in subject), 'default')
    base = PLACEHOLDER_RESPONSES[key]
    return f"🔬 **Study Companion (Demo Mode)**\n\n{base}\n\n_Add your AI API key in Profile → Settings to get full personalized responses._"


def _call_ai(api_key, provider, conversation, user_text):
    """Call real AI API — Gemini or OpenAI compatible."""
    messages_history = list(conversation.messages.order_by('timestamp').values('role', 'content'))
    system_prompt = "You are Libria, an expert study companion for Ethiopian high-school students. Help students understand concepts deeply — don't just give answers. Ask guiding questions, provide examples, and encourage active thinking. Be concise, encouraging, and educational."

    try:
        if provider == 'gemini':
            import requests as req
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
            contents = []
            for m in messages_history[-10:]:
                role = 'user' if m['role'] == 'user' else 'model'
                contents.append({'role': role, 'parts': [{'text': m['content']}]})
            payload = {'contents': contents, 'systemInstruction': {'parts': [{'text': system_prompt}]}}
            r = req.post(url, json=payload, timeout=15)
            return r.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            import requests as req
            headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
            msgs = [{'role': 'system', 'content': system_prompt}]
            for m in messages_history[-10:]:
                msgs.append({'role': m['role'], 'content': m['content']})
            payload = {'model': 'gpt-4o-mini', 'messages': msgs}
            r = req.post('https://api.openai.com/v1/chat/completions', json=payload,
                         headers=headers, timeout=15)
            return r.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"⚠️ AI response error: {str(e)[:100]}. Please check your API key in Profile settings."
