// static/js/chat.js
document.addEventListener('DOMContentLoaded', function () {
    const chatForm = document.getElementById('chatForm');
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const enableKnowledgeBase = document.getElementById('enableKnowledgeBase');
    const knowledgeBaseSelection = document.getElementById('knowledgeBaseSelection');
    const knowledgeBaseSelect = document.getElementById('knowledgeBaseSelect');
    const clearButton = document.getElementById('clearChat'); // 新增清空按钮元素

    // 初始化代码高亮，使用深色主题
    hljs.configure({
        languages: ['python', 'javascript', 'html', 'css', 'json'],
        tabReplace: '    ',
        cssSelector: 'pre code' // 添加这行
    });
    hljs.initHighlightingOnLoad();

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
        let segments = [];  // 用于存储文本段和代码块段
        let tempContent = content;
        let codeBlockStart = tempContent.indexOf('```');

        // 先将内容分割成文本段和代码块段
        while (codeBlockStart !== -1) {
            // 添加代码块前的文本
            if (codeBlockStart > 0) {
                segments.push({
                    type: 'text',
                    content: tempContent.substring(0, codeBlockStart)
                });
            }

            // 找到代码块的结束位置
            let codeBlockEnd = tempContent.indexOf('```', codeBlockStart + 3);

            if (codeBlockEnd !== -1) {
                // 提取语言标识
                let firstLineEnd = tempContent.indexOf('\n', codeBlockStart);
                let language = tempContent.substring(codeBlockStart + 3, firstLineEnd).trim();

                // 提取代码内容
                let code = tempContent.substring(firstLineEnd + 1, codeBlockEnd);

                segments.push({
                    type: 'code',
                    language: language,
                    content: code
                });

                // 更新剩余内容
                tempContent = tempContent.substring(codeBlockEnd + 3);
                codeBlockStart = tempContent.indexOf('```');
            } else {
                // 未闭合的代码块，作为文本处理
                segments.push({
                    type: 'text',
                    content: tempContent.substring(codeBlockStart)
                });
                break;
            }
        }

        // 添加剩余的文本
        if (tempContent && codeBlockStart === -1) {
            segments.push({
                type: 'text',
                content: tempContent
            });
        }

        // 清空元素内容
        element.innerHTML = '';

        // 创建包装容器
        const wrapper = document.createElement('div');
        wrapper.className = 'message-content-wrapper';
        element.appendChild(wrapper);

        // 逐段处理内容
        segments.forEach(segment => {
            if (segment.type === 'text') {
                const textDiv = document.createElement('div');
                textDiv.className = 'text-content';
                textDiv.textContent = segment.content;
                wrapper.appendChild(textDiv);
            } else if (segment.type === 'code') {
                const preElement = document.createElement('pre');
                const codeElement = document.createElement('code');

                // 设置语言类
                codeElement.className = `language-${segment.language} hljs`;

                // 清理代码内容，移除多余的空白
                const cleanedCode = segment.content.trim();
                codeElement.textContent = cleanedCode;

                // 添加到 DOM
                preElement.appendChild(codeElement);
                wrapper.appendChild(preElement);

                // 应用高亮
                hljs.highlightElement(codeElement);
            }
        });
    }

    // 添加消息到聊天界面
    function appendMessage(content, isUser) {
        const divider = document.createElement('div');
        divider.className = 'message-divider';
        chatMessages.appendChild(divider);

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;

        // 添加头像（使用默认图标作为后备）
        const avatarContainer = document.createElement('div');
        avatarContainer.className = 'avatar';

        // 创建图片元素
        const avatarImg = document.createElement('img');
        // avatarImg.className = 'avatar-img';
        avatarImg.src = isUser ? '/static/img/user-avatar.png' : '/static/img/ai-avatar.png';
        avatarImg.alt = isUser ? '用户' : 'AI助手';

        // 添加图片加载错误处理
        avatarImg.onerror = function () {
            this.style.display = 'none';
            // 根据角色使用不同的图标
            const iconClass = isUser ? 'fa-user' : 'fa-robot';
            avatarContainer.innerHTML = `<i class="fas ${iconClass}"></i>`;
        };

        // 确保图片加载完成后再添加到容器
        avatarImg.onload = function () {
            this.style.display = 'block';
        };

        avatarContainer.appendChild(avatarImg);

        // 添加内容容器
        const contentDiv = document.createElement('div');
        contentDiv.className = 'content';

        if (isUser) {
            contentDiv.textContent = content;
        } else {
            processStreamContent(content, contentDiv);
        }

        messageDiv.appendChild(avatarContainer);
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // 优化输入框自适应高度功能
    function initializeTextarea() {
        const textarea = document.getElementById('userInput');

        // 设置初始高度
        function updateHeight() {
            textarea.style.height = 'auto';
            textarea.style.height = Math.max(24, Math.min(150, textarea.scrollHeight)) + 'px';
        }

        // 监听输入事件
        textarea.addEventListener('input', updateHeight);

        // 监听键盘事件
        textarea.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const form = document.getElementById('chatForm');
                if (form) {
                    form.dispatchEvent(new Event('submit'));
                }
                // 重置输入框高度
                this.style.height = '24px';
            }
        });

        // 初始化高度
        updateHeight();
    }


    // 创建消息元素
    function createMessageElement(isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
        return messageDiv;
    }

    // 发送消息并处理流式响应
    // 修改 sendStreamMessage 函数中创建消息的部分
    async function sendStreamMessage(query) {
        appendMessage(query, true);  // 用户消息

        // 创建完整的 AI 消息结构
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant';

        // 创建头像容器
        const avatarContainer = document.createElement('div');
        avatarContainer.className = 'avatar';

        // 添加默认图标
        const iconElement = document.createElement('i');
        iconElement.className = 'fas fa-robot';
        avatarContainer.appendChild(iconElement);

        // 尝试加载 AI 头像图片
        const avatarImg = new Image();
        avatarImg.src = '/static/img/ai-avatar.png';
        avatarImg.className = 'avatar-img';

        avatarImg.onload = function () {
            // 图片加载成功，替换图标
            avatarContainer.innerHTML = '';
            avatarContainer.appendChild(avatarImg);
        };

        // 创建内容容器
        const contentDiv = document.createElement('div');
        contentDiv.className = 'content';

        // 组装消息结构
        messageDiv.appendChild(avatarContainer);
        messageDiv.appendChild(contentDiv);
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
                                contentDiv.innerHTML = `<div class="error-message">错误: ${data.error}</div>`;
                                return;
                            }

                            if (data.type === 'content') {
                                fullContent += data.content;
                                processStreamContent(fullContent, contentDiv);

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
            contentDiv.innerHTML = `<div class="error-message">发送消息失败: ${error.message}</div>`;
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

    // 清空对话历史记录
    function clearChat() {
        if (confirm('确定要清空所有对话吗？')) {
            chatMessages.innerHTML = '';
            chatHistory = [];
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

    // 添加清空按钮事件监听器
    if (clearButton) {
        clearButton.addEventListener('click', clearChat);
    }

    userInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });

    // 输入框自动调整高度
    userInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    initializeTextarea();
});