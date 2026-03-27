import json
from django.shortcuts import render
from .lru_cache import LRUCache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

obj = LRUCache(5)
log = []


def log_op(operation, key=None, value=None, status='success'):
    log_entry = {
        'id': len(log) + 1,
        'operation': operation.upper(),
        'key': key,
        'value': value,
        'status': status,
        # Store as formatted string so it's JSON-serializable
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    log.append(log_entry)


@csrf_exempt
def home(request):
    return render(request, 'index.html')


@csrf_exempt
def add_item(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    data = json.loads(request.body)
    key = data.get('key')
    value = data.get('value')

    if key is None or value is None:
        log_op('PUT', key, value, status='error')
        return JsonResponse({'error': 'Key and value are required'}, status=400)

    obj.put(key, value)
    log_op('PUT', key, value, status='success')
    return JsonResponse({'message': f'Item "{key}" added successfully'})


@csrf_exempt
def get_item(request):
    # Use POST so we can safely send a JSON body (GET + body is unreliable)
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    data = json.loads(request.body)
    key = data.get('key')

    if not key:
        log_op('GET', status='error')
        return JsonResponse({'error': 'Key required'}, status=400)

    value = obj.get(key)
    if value is not None:
        log_op('GET', key=key, value=value, status='hit')
        return JsonResponse({'key': key, 'value': value})
    else:
        log_op('GET', key=key, status='miss')
        return JsonResponse({'error': 'Key not found'}, status=404)


@csrf_exempt
def delete_item(request):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    data = json.loads(request.body)
    key = data.get('key')

    if not key:
        log_op('DELETE', status='error')
        return JsonResponse({'error': 'Key required'}, status=400)

    # Fix: use obj.delete(), not cache.delete()
    success = obj.delete(key)
    if success:
        log_op('DELETE', key=key, status='success')
        return JsonResponse({'message': f'"{key}" deleted successfully'})
    else:
        log_op('DELETE', key=key, status='miss')
        return JsonResponse({'error': 'Key not found'}, status=404)


@csrf_exempt
def clear_cache(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    # Fix: use obj.clear(), not cache.clear()
    obj.clear()
    log_op('CLEAR', status='success')
    return JsonResponse({'message': 'Cache cleared successfully'})


def view_logs(request):
    # log entries are already JSON-safe (timestamp is a string)
    return JsonResponse({'logs': log})


def get_all_items(request):
    items = obj.get_all()
    return JsonResponse({'items': items})