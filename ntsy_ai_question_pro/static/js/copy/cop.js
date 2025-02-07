// static/js/chat.js
document.addEventListener('DOMContentLoaded', function () {
    const chatForm = document.getElementById('chatForm');
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const enableKnowledgeBase = document.getElementById('enableKnowledgeBase');
    const knowledgeBaseSelection = document.getElementById('knowledgeBaseSelection');
    const knowledgeBaseSelect = document.getElementById('knowledgeBaseSelect');

    // 初始化代码高亮，使用深色主题
    hljs.configure({
        languages: ['python', 'javascript', 'html', 'css', 'json'],
        tabReplace: '    '
    });

    const API_ENDPOINTS = {
        CHAT: '/chat/api/chat',
        CHAT_STREAM: '/chat/api/chat/stream',
        KNOWLEDGE_LIST: '/knowledge/api/knowledge/list'
    };

    let chatHistory = [];
    let currentCodeBlock = '';
    let isInCodeBlock = false;
    let codeLanguage = '';

    // 处理流式内容
    function processStreamContent(content, element) {
        let formattedContent = '';
        let tempContent = content;
        let codeBlockStart = tempContent.indexOf('```');

        while (codeBlockStart !== -1) {
            // 处理代码块之前的普通文本
            if (codeBlockStart > 0) {
                formattedContent += tempContent.substring(0, codeBlockStart);
            }

            // 找到代码块的结束位置
            let codeBlockEnd = tempContent.indexOf('```', codeBlockStart + 3);
            
            if (codeBlockEnd !== -1) {
                // 提取语言标识
                let firstLineEnd = tempContent.indexOf('\n', codeBlockStart);
                let language = tempContent.substring(codeBlockStart + 3, firstLineEnd).trim();
                
                // 提取代码内容
                let code = tempContent.substring(firstLineEnd + 1, codeBlockEnd);
                
                // 创建代码块HTML
                formattedContent += `<pre><code class="language-${language} hljs">${code}</code></pre>`;
                
                // 更新剩余内容
                tempContent = tempContent.substring(codeBlockEnd + 3);
                codeBlockStart = tempContent.indexOf('```');
            } else {
                // 未闭合的代码块，保持原样
                formattedContent += tempContent.substring(codeBlockStart);
                break;
            }
        }

        // 添加剩余的普通文本
        if (codeBlockStart === -1) {
            formattedContent += tempContent;
        }

        // 更新元素内容
        element.innerHTML = formattedContent;

        // 对所有代码块应用高亮
        element.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightBlock(block);
        });
    }

    // 添加消息到聊天界面
    function appendMessage(content, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
        if (isUser) {
            messageDiv.textContent = content;
        } else {
            processStreamContent(content, messageDiv);
        }
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // 创建消息元素
    function createMessageElement(isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
        return messageDiv;
    }

    // 发送消息并处理流式响应
    async function sendStreamMessage(query) {
        appendMessage(query, true);
        const messageDiv = createMessageElement(false);
        chatMessages.appendChild(messageDiv);

        try {
            const response = await fetch(API_ENDPOINTS.CHAT_STREAM, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query,
                    history: chatHistory,
                    knowledge_base: enableKnowledgeBase.checked ? knowledgeBaseSelect.value : null
                })
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let fullContent = '';

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));

                            if (data.error) {
                                messageDiv.innerHTML = `<div class="error-message">错误: ${data.error}</div>`;
                                return;
                            }

                            if (data.type === 'content') {
                                fullContent += data.content;
                                processStreamContent(fullContent, messageDiv);

                                if (data.done) {
                                    chatHistory.push(
                                        { role: "user", content: query },
                                        { role: "assistant", content: fullContent }
                                    );
                                }
                            }
                        } catch (e) {
                            console.error('Error parsing SSE data:', e);
                        }
                    }
                }

                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        } catch (error) {
            console.error('Stream Error:', error);
            messageDiv.innerHTML = `<div class="error-message">发送消息失败: ${error.message}</div>`;
        }
    }

    // 加载知识库列表
    async function loadKnowledgeBases() {
        try {
            const response = await axios.get(API_ENDPOINTS.KNOWLEDGE_LIST);
            const bases = response.data;
            knowledgeBaseSelect.innerHTML = '<option value="">请选择知识库...</option>';
            bases.forEach(base => {
                const option = document.createElement('option');
                option.value = base.name;
                option.textContent = base.name;
                knowledgeBaseSelect.appendChild(option);
            });
        } catch (error) {
            console.error('加载知识库失败:', error);
        }
    }

    // 事件监听器设置
    enableKnowledgeBase.addEventListener('change', function () {
        knowledgeBaseSelection.classList.toggle('d-none', !this.checked);
        if (this.checked) {
            loadKnowledgeBases();
        }
    });

    chatForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const query = userInput.value.trim();
        if (!query) return;

        userInput.value = '';
        await sendStreamMessage(query);
    });

    userInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });

    // 输入框自动调整高度
    userInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
});