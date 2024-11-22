document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    
    const PLACEHOLDER_IMAGE = "{% static 'lostitems/images/placeholder.svg' %}";
    let currentItem = null;

    const itemsContainer = document.getElementById('itemsContainer');
    const reportButton = document.getElementById('reportButton');
    const modal = document.getElementById('modal');
    const detailModal = document.getElementById('detailModal');
    const reportForm = document.getElementById('reportForm');

    // Fetch all items from the backend
    async function fetchItems() {
        try {
            const response = await fetch('/api/items/');
            const data = await response.json();
            return data.items;
        } catch (error) {
            console.error('Error fetching items:', error);
            return [];
        }
    }

    // Fetch messages for a specific item
    async function fetchMessages(itemId) {
        try {
            const response = await fetch(`/api/items/${itemId}/messages/`);
            const data = await response.json();
            return data.messages;
        } catch (error) {
            console.error('Error fetching messages:', error);
            return [];
        }
    }

    function createItemCard(item) {
        const card = document.createElement('div');
        card.className = 'item-card';
        card.innerHTML = `
            <img src="${item.image || PLACEHOLDER_IMAGE}" alt="${item.title}" class="item-image" onerror="this.src='${PLACEHOLDER_IMAGE}'">
            <div class="item-content">
                <h2 class="item-title">${item.title}</h2>
                <p class="item-details">
                    <i data-lucide="map-pin"></i> ${item.location}<br>
                    <i data-lucide="calendar"></i> ${item.date}
                </p>
            </div>
        `;
        
        card.addEventListener('click', () => showItemDetails(item));
        return card;
    }

    async function showItemDetails(item) {
        currentItem = item;
        const detailContent = document.querySelector('.detail-modal-content');
        detailContent.innerHTML = `
            <h2>${item.title}</h2>
            <img src="${item.image || PLACEHOLDER_IMAGE}" alt="${item.title}" class="detail-image" onerror="this.src='${PLACEHOLDER_IMAGE}'">
            <p><strong>Location:</strong> ${item.location}</p>
            <p><strong>Date:</strong> ${item.date}</p>
            <p><strong>Description:</strong> ${item.description || 'No description available'}</p>
            <div class="detail-buttons">
                <button class="chat-button">
                    <i data-lucide="message-circle"></i>
                    Chat with Finder
                </button>
                <button class="close-button">Close</button>
            </div>
        `;
        
        detailModal.style.display = 'block';
        
        const closeButton = detailContent.querySelector('.close-button');
        const chatButton = detailContent.querySelector('.chat-button');
        
        closeButton.addEventListener('click', () => {
            detailModal.style.display = 'none';
        });

        chatButton.addEventListener('click', () => {
            showChat(item);
        });

        lucide.createIcons();
    }

    async function showChat(item) {
        const chatModal = document.getElementById('chatModal');
        const chatMessages = document.getElementById('chatMessages');
        const chatForm = document.getElementById('chatForm');

        chatModal.style.display = 'block';
        
        // Fetch and render messages
        const messages = await fetchMessages(item.id);
        renderMessages(messages);

        chatForm.onsubmit = async (e) => {
            e.preventDefault();
            const messageInput = document.getElementById('messageInput');
            const messageText = messageInput.value.trim();
            
            if (messageText) {
                try {
                    const response = await fetch(`/api/items/${item.id}/messages/create/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            text: messageText,
                            sender: 'user'
                        })
                    });
                    
                    if (response.ok) {
                        const messages = await fetchMessages(item.id);
                        renderMessages(messages);
                        messageInput.value = '';
                    }
                } catch (error) {
                    console.error('Error sending message:', error);
                }
            }
        };

        window.addEventListener('click', (event) => {
            if (event.target === chatModal) {
                chatModal.style.display = 'none';
            }
        });
    }

    function renderMessages(messages) {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = messages.length ? '' : '<p class="no-messages">No messages yet</p>';
        
        messages.forEach(message => {
            const messageElement = document.createElement('div');
            messageElement.className = `message ${message.sender}`;
            messageElement.innerHTML = `
                <p class="message-text">${message.text}</p>
                <span class="message-time">${new Date(message.timestamp).toLocaleTimeString()}</span>
            `;
            chatMessages.appendChild(messageElement);
        });
        
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function renderItems() {
        const items = await fetchItems();
        itemsContainer.innerHTML = '';
        items.forEach(item => {
            const card = createItemCard(item);
            itemsContainer.appendChild(card);
        });
        lucide.createIcons();
    }

    reportButton.addEventListener('click', () => {
        modal.style.display = 'block';
    });

    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
        if (event.target === detailModal) {
            detailModal.style.display = 'none';
        }
    });

    reportForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const formData = new FormData();
        formData.append('title', document.getElementById('title').value);
        formData.append('description', document.getElementById('description').value);
        formData.append('location', document.getElementById('location').value);
        formData.append('image', document.getElementById('image').files[0]);

        try {
            const response = await fetch('/api/items/create/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                },
                body: formData
            });

            if (response.ok) {
                await renderItems();
                modal.style.display = 'none';
                reportForm.reset();
            } else {
                console.error('Error creating item:', await response.text());
            }
        } catch (error) {
            console.error('Error creating item:', error);
        }
    });

    renderItems();
});

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

