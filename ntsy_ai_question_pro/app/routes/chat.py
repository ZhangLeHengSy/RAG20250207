# app/routes/chat.py
import asyncio
from flask import Blueprint, render_template, request, jsonify, current_app, Response, stream_with_context
import json

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/')
def index():
    return render_template('chat.html')

# @chat_bp.route('/api/chat', methods=['POST'])
# def chat():
#     print("Received chat request")
#     print(f"Request data: {request.json}")
#     data = request.json
#     query = data.get('query')
#     history = data.get('history', [])
#     knowledge_base = data.get('knowledge_base')
    
#     if not query:
#         return jsonify({"error": "Query is required"}), 400
    
#     try:
#         # 直接调用 chat_service 并返回结果
#         response = current_app.chat_service.chat(
#             query=query,
#             history=history,
#             knowledge_base=knowledge_base
#         )
#         return jsonify(response)
#     except Exception as e:
#         print(f"Chat error: {str(e)}")
#         return jsonify({"error": str(e)}), 500
    
@chat_bp.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    print("Received stream chat request")
    data = request.json
    query = data.get('query')
    history = data.get('history', [])
    knowledge_base = data.get('knowledge_base')
    
    if not query:
        return jsonify({"error": "Query is required"}), 400

    def generate():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            async def process_stream():
                async for chunk in current_app.chat_service.stream_chat(
                    query=query,
                    history=history,
                    knowledge_base=knowledge_base
                ):
                    yield f"data: {json.dumps(chunk)}\n\n"

            # 运行异步代码
            gen = process_stream()
            while True:
                try:
                    chunk = loop.run_until_complete(gen.__anext__())
                    yield chunk
                except StopAsyncIteration:
                    break
                
        except Exception as e:
            print(f"Stream chat error: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            loop.close()

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )