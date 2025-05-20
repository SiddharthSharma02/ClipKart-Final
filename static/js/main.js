// Video processing functionality
document.addEventListener('DOMContentLoaded', function() {
    const videoForm = document.getElementById('videoForm');
    const submitBtn = document.getElementById('submitBtn');
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const outputContainer = document.getElementById('outputContainer');
    const outputVideo = document.getElementById('outputVideo');
    const videoPlaceholder = document.querySelector('.output-preview .placeholder');
    const downloadBtn = document.getElementById('downloadBtn');
    const shareBtn = document.getElementById('shareBtn');
    const errorMessage = document.getElementById('errorMessage');

    // Form submission
    videoForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const url = document.getElementById('youtubeUrl').value;
        const file = document.getElementById('videoFile')?.files[0];
        const duration = document.getElementById('duration').value;
        const format = document.getElementById('format').value;
        const captions = document.getElementById('captions').checked;

        if (!url && !file) {
            showError('Please enter a YouTube URL or upload a video file');
            return;
        }

        // Show loading state
        submitBtn.classList.add('loading');
        document.querySelector('.video-input').classList.add('loading');
        errorMessage.style.display = 'none';
        progressContainer.style.display = 'block';
        outputContainer.style.display = 'none';

        // Declare interval in the outer scope so it can be accessed in the catch block
        let interval;
        let taskId = null;

        try {
            // Prepare form data
            const formData = new FormData(videoForm);
            
            // Start progress animation for visual feedback during initial request
            let progress = 0;
            interval = setInterval(() => {
                if (progress < 10) {
                    progress += 1;
                    updateProgress(progress, "Preparing...");
                }
            }, 500);

            // Submit the form data
            const response = await fetch('/process', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Failed to process video');
            }

            // Clear the visual loading interval
            clearInterval(interval);
            
            // Store the task ID for polling
            taskId = data.task_id;
            
            // Start polling for status updates
            pollTaskStatus(taskId);

        } catch (error) {
            showError(error.message || 'An error occurred');
            if (interval) clearInterval(interval);
            resetUI();
        }
    });

    // Poll task status
    function pollTaskStatus(taskId) {
        const statusInterval = setInterval(async () => {
            try {
                const response = await fetch(`/status/${taskId}`);
                const data = await response.json();
                
                if (!data.success) {
                    throw new Error(data.error || 'Failed to check status');
                }
                
                // Update progress
                updateProgress(
                    data.progress, 
                    data.current_stage || 'Processing...'
                );
                
                // Handle completion or failure
                if (data.status === 'completed') {
                    clearInterval(statusInterval);
                    
                    // Update UI with processed video
                    outputVideo.src = data.download_url;
                    downloadBtn.onclick = () => window.location.href = data.download_url;
                    shareBtn.onclick = () => shareVideo(window.location.origin + data.download_url);
                    
                    completeProcessing();
                } else if (data.status === 'failed') {
                    clearInterval(statusInterval);
                    throw new Error(data.error || 'Processing failed');
                }
                
            } catch (error) {
                clearInterval(statusInterval);
                showError(error.message || 'An error occurred');
                resetUI();
            }
        }, 1000); // Check every second
    }

    function updateProgress(progress, message = null) {
        progressBar.style.width = `${progress}%`;
        progressText.textContent = message || `Processing... ${progress}%`;
    }

    function completeProcessing() {
        progressContainer.style.display = 'none';
        outputContainer.style.display = 'block';
        videoPlaceholder.style.display = 'none';
        outputVideo.style.display = 'block';
        submitBtn.classList.remove('loading');
        document.querySelector('.video-input').classList.remove('loading');
    }

    function resetUI() {
        submitBtn.classList.remove('loading');
        document.querySelector('.video-input').classList.remove('loading');
        progressContainer.style.display = 'none';
        outputContainer.style.display = 'none';
    }

    function showError(message) {
        const errorMessageElement = document.getElementById('errorMessageText');
        errorMessageElement.textContent = message;
        errorMessage.style.display = 'block';
        
        // Scroll to the error message
        errorMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function shareVideo(url) {
        if (navigator.share) {
            navigator.share({
                title: 'Check out this video!',
                url: url
            }).catch(console.error);
        } else {
            // Fallback for browsers that don't support Web Share API
            const tempInput = document.createElement('input');
            document.body.appendChild(tempInput);
            tempInput.value = url;
            tempInput.select();
            document.execCommand('copy');
            document.body.removeChild(tempInput);
            alert('Link copied to clipboard!');
        }
    }

    // Chatbot functionality
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const chatMessages = document.getElementById('chatMessages');
    const sendButton = document.getElementById('sendButton');

    chatForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const message = chatInput.value.trim();
        
        if (!message) return;

        // Add user message to chat
        addMessage(message, 'user');
        chatInput.value = '';

        try {
            // Show loading state
            sendButton.disabled = true;
            sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            // Add AI response to chat
            addMessage(data.response, 'ai');

        } catch (error) {
            addMessage('Sorry, there was an error processing your message.', 'error');
        } finally {
            // Reset button state
            sendButton.disabled = false;
            sendButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
        }
    });

    function addMessage(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${type}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = text;
        
        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}); 