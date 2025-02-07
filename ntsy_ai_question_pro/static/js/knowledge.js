// static/js/knowledge.js
document.addEventListener('DOMContentLoaded', function () {
    const createCategoryForm = document.getElementById('createCategoryForm');
    const createForm = document.getElementById('createKnowledgeBaseForm');
    const uploadForm = document.getElementById('uploadForm');
    const knowledgeBaseSelect = document.getElementById('knowledgeBaseSelect');
    const categorySelect = document.getElementById('categorySelect');
    const categoryList = document.getElementById('categoryList');

    let categories = [];
    let selectedCategory = '';

    const API_BASE = '/knowledge/api';  // 添加这行
    const API_ENDPOINTS = {
        CATEGORIES_LIST: `${API_BASE}/knowledge/categories`,
        CATEGORIES_CREATE: `${API_BASE}/knowledge/categories/create`,
        KNOWLEDGE_LIST: `${API_BASE}/knowledge/list`,
        KNOWLEDGE_CREATE: `${API_BASE}/knowledge/create`,
        KNOWLEDGE_UPLOAD: `${API_BASE}/knowledge/upload`,
        KNOWLEDGE_DELETE: `${API_BASE}/knowledge/delete`,
        KNOWLEDGE_INFO: (name) => `${API_BASE}/knowledge/${name}/info`
    };
    loadCategories();

    loadKnowledgeBases();
    // 加载知识库列表
    async function loadCategories() {
        try {
            const response = await axios.get(API_ENDPOINTS.CATEGORIES_LIST);
            categories = response.data;
            updateCategoryUI();
        } catch (error) {
            console.error('加载分类失败:', error);
            alert('加载分类失败: ' + (error.response?.data?.error || error.message));
        }
    }

    // 创建分类
    // createCategoryForm.addEventListener('submit', async function (e) {
    //     e.preventDefault();
    //     const name = document.getElementById('categoryName').value.trim();

    //     if (!name) {
    //         alert('分类名称不能为空');
    //         return;
    //     }

    //     try {
    //         await axios.post(API_ENDPOINTS.CATEGORIES_CREATE, { name });
    //         alert('分类创建成功');
    //         loadCategories();  // 重新加载分类列表
    //         document.getElementById('categoryName').value = '';  // 清空输入框
    //     } catch (error) {
    //         console.error('创建分类失败:', error);
    //         alert('创建分类失败: ' + (error.response?.data?.error || error.message));
    //     }
    // });

    // 删除分类
    async function deleteCategory(categoryId) {
        if (!confirm('确定要删除这个分类吗？')) {
            return;
        }

        try {
            await axios.delete(`${API_ENDPOINTS.CATEGORIES_DELETE}/${categoryId}`);
            alert('分类删除成功');
            loadCategories();  // 重新加载分类列表
        } catch (error) {
            console.error('删除分类失败:', error);
            alert('删除分类失败: ' + (error.response?.data?.error || error.message));
        }
    }

    // 更新分类UI
    function updateCategoryUI() {
        // 更新分类选择下拉框
        categorySelect.innerHTML = '<option value="">请选择分类...</option>';
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.id;
            option.textContent = category.name;
            categorySelect.appendChild(option);
        });

        // 更新分类标签列表
        categoryList.innerHTML = '';
        categories.forEach(category => {
            const badge = document.createElement('span');
            badge.className = `category-badge ${category.id === selectedCategory ? 'active' : ''}`;
            badge.textContent = category.name;
            badge.onclick = () => selectCategory(category.id);
            categoryList.appendChild(badge);
        });
    }

    // 选择分类
    function selectCategory(categoryId) {
        selectedCategory = categoryId;
        updateCategoryUI();
        loadKnowledgeBases(categoryId);
    }


    // 创建分类
    createCategoryForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const name = document.getElementById('categoryName').value;

        try {
            // 确保设置正确的 Content-Type
            const response = await axios.post('/knowledge/api/knowledge/categories/create', 
                { name: name },
                {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );
            
            if (response.data) {
                alert('分类创建成功');
                loadCategories();
                document.getElementById('categoryName').value = '';
            }
        } catch (error) {
            console.error('创建分类失败:', error);
            alert('创建分类失败: ' + (error.response?.data?.error || error.message));
        }
    });

    // 加载知识库列表
    async function loadKnowledgeBases(categoryId = '') {
        try {
            const response = await axios.get(`/knowledge/api/knowledge/list${categoryId ? '?category=' + categoryId : ''}`);
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
            alert('加载知识库失败');
        }
    }

    // 创建知识库
    createForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const name = document.getElementById('knowledgeBaseName').value;
        const categoryId = document.getElementById('categorySelect').value;

        if (!name) {
            alert('知识库名称不能为空');
            return;
        }
    

        if (!categoryId) {
            alert('请选择分类');
            return;
        }
    
        try {
            const response = await axios.post('/knowledge/api/knowledge/create', 
                {
                    name: name,
                    categoryId: categoryId
                },
                {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );
    
            if (response.data.message) {
                alert('知识库创建成功');
                // 清空输入
                document.getElementById('knowledgeBaseName').value = '';
                document.getElementById('categorySelect').value = '';
                // 重新加载知识库列表
                await loadKnowledgeBases();
            }
        } catch (error) {
            console.error('创建知识库失败:', error);
            alert('创建知识库失败: ' + (error.response?.data?.error || error.message));
        }
    });

    // 上传文件
    uploadForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const files = document.getElementById('files').files;
        const knowledgeBase = knowledgeBaseSelect.value;

        if (!knowledgeBase) {
            alert('请选择知识库');
            return;
        }

        const formData = new FormData();
        formData.append('knowledge_base', knowledgeBase);
        Array.from(files).forEach(file => {
            formData.append('files[]', file);
        });

        const progressBar = document.querySelector('#uploadProgress');
        progressBar.classList.remove('d-none');

        try {
            await axios.post('/knowledge/api/knowledge/upload', formData, {
                onUploadProgress: (progressEvent) => {
                    const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                    progressBar.querySelector('.progress-bar').style.width = percentCompleted + '%';
                }
            });

            alert('文件上传成功');
            uploadForm.reset();
            progressBar.classList.add('d-none');
        } catch (error) {
            console.error('上传文件失败:', error);
            alert('上传文件失败');
            progressBar.classList.add('d-none');
        }
    });

    // 删除知识库
    async function deleteKnowledgeBase(name) {
        if (!confirm(`确定要删除知识库 "${name}" 吗？这个操作不可撤销。`)) {
            return;
        }

        try {
            await axios.post('/knowledge/api/knowledge/delete', { name });
            alert('知识库删除成功');
            loadKnowledgeBases();
        } catch (error) {
            console.error('删除知识库失败:', error);
            alert('删除知识库失败: ' + (error.response?.data?.error || error.message));
        }
    }

    // 获取知识库信息
    async function getKnowledgeBaseInfo(name) {
        try {
            const response = await axios.get(`/knowledge/api/knowledge/${name}/info`);
            const info = response.data;

            // 更新UI显示知识库信息
            const infoDiv = document.getElementById('knowledgeBaseInfo');
            if (infoDiv) {
                infoDiv.innerHTML = `
                <div class="card-body">
                    <h5 class="card-title">${info.name}</h5>
                    <p class="card-text">文档数量: ${info.document_count}</p>
                    <p class="card-text">创建时间: ${new Date(info.created_at * 1000).toLocaleString()}</p>
                    <button class="btn btn-danger btn-sm" onclick="deleteKnowledgeBase('${info.name}')">
                        删除知识库
                    </button>
                </div>
            `;
            }
        } catch (error) {
            console.error('获取知识库信息失败:', error);
        }
    }

    // 在知识库选择变化时更新信息
    knowledgeBaseSelect.addEventListener('change', function () {
        const selectedBase = this.value;
        if (selectedBase) {
            getKnowledgeBaseInfo(selectedBase);
        }
    });

    // 初始加载知识库列表
    loadKnowledgeBases();
});