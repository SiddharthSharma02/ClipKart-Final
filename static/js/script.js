document.addEventListener('DOMContentLoaded', function() {
    const videoForm = document.getElementById('videoForm');
    const progressContainer = document.getElementById('progressContainer');
    const statusText = document.getElementById('statusText');
    const downloadProgress = document.getElementById('downloadProgress');
    const processProgress = document.getElementById('processProgress');
    const percentageText = document.getElementById('percentageText');
    const downloadSection = document.getElementById('downloadSection');
    const errorSection = document.getElementById('errorSection');
    const downloadLink = document.getElementById('downloadLink');
    const errorText = document.getElementById('errorText');
    const retryBtn = document.getElementById('retryBtn');
    const newVideoBtn = document.getElementById('newVideoBtn');
    const youtubeUrlInput = document.getElementById('youtubeUrl');
    const durationInput = document.getElementById('duration');
    const formatSelect = document.getElementById('format');
    const outputPathInput = document.getElementById('outputPath');
    const browseBtn = document.getElementById('browseBtn');
    const fileLocation = document.getElementById('fileLocation');
    const filePath = document.getElementById('filePath');
    const submitBtn = document.getElementById('submitBtn');
    const videoInput = document.querySelector('.video-input');
    const estimatedTimeEl = document.getElementById('estimatedTime');
    
    let currentTaskId = null;
    let statusCheckInterval = null;
    let startTime = null;
    let lastProgress = 0;
    let progressHistory = [];
    
    // Add folder browse functionality if supported by the browser
    browseBtn.addEventListener('click', function() {
        // Show a loading state on the button
        const originalText = browseBtn.textContent;
        browseBtn.disabled = true;
        browseBtn.textContent = 'Opening...';
        
        // Call the server-side browse folder endpoint
        fetch('/browse-folder')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    outputPathInput.value = data.folder;
                    
                    if (data.default) {
                        showToast('Using default output folder: ' + data.folder, 'warning');
                    } else {
                        showToast('Output folder selected: ' + data.folder, 'success');
                    }
                } else {
                    showToast('Failed to select folder: ' + (data.error || 'No folder selected'), 'error');
                }
            })
            .catch(error => {
                console.error('Browse error:', error);
                showToast('Error browsing for folder: ' + error.message, 'error');
            })
            .finally(() => {
                // Reset button state
                browseBtn.disabled = false;
                browseBtn.textContent = originalText;
            });
    });
    
    // Submit form
    videoForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form values
        const url = youtubeUrlInput.value.trim();
        const duration = durationInput.value.trim() || '60';
        const format = formatSelect.value;
        const outputPath = outputPathInput.value.trim();
        const captions = document.getElementById('captions').checked;
        
        // Validate inputs
        if (!url) {
            showToast('Please enter a YouTube URL', 'error');
            return;
        }
        
        if (!outputPath) {
            showToast('Please select an output folder', 'error');
            return;
        }
        
        // Show loading state
        submitBtn.disabled = true;
        submitBtn.textContent = 'Processing...';
        
        // Hide the form and show progress
        videoInput.style.display = 'none';
        progressContainer.style.display = 'block';
        downloadSection.style.display = 'none';
        errorSection.style.display = 'none';
        
        // Reset progress tracking
        startTime = Date.now();
        lastProgress = 0;
        progressHistory = [];
        
        // Submit the video for processing with all required parameters
        submitVideo(url, duration, format, outputPath, captions);
    });
    
    // Check if URL is a valid YouTube URL
    function isValidYoutubeUrl(url) {
        const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+/;
        return youtubeRegex.test(url);
    }
    
    // Calculate estimated time remaining
    function calculateEstimatedTime(progress) {
        if (progress <= 0 || !startTime) return 'Calculating...';
        
        // Store progress and time for more accurate estimation
        const currentTime = Date.now();
        const elapsedTime = (currentTime - startTime) / 1000; // in seconds
        
        // Add to history (store last 5 points for calculation)
        progressHistory.push({progress, time: elapsedTime});
        if (progressHistory.length > 5) {
            progressHistory.shift();
        }
        
        // Need at least 2 points to calculate rate
        if (progressHistory.length < 2) {
            return 'Calculating...';
        }
        
        // Calculate progress rate using recent history
        const oldestPoint = progressHistory[0];
        const latestPoint = progressHistory[progressHistory.length - 1];
        const progressDiff = latestPoint.progress - oldestPoint.progress;
        const timeDiff = latestPoint.time - oldestPoint.time;
        
        // Avoid division by zero or negative progress
        if (timeDiff <= 0 || progressDiff <= 0) return 'Calculating...';
        
        // Calculate progress rate per second
        const progressRate = progressDiff / timeDiff;
        
        // Calculate remaining time
        const remainingProgress = 100 - progress;
        const estimatedSeconds = remainingProgress / progressRate;
        
        // Format time
        if (estimatedSeconds < 60) {
            return `About ${Math.round(estimatedSeconds)} seconds`;
        } else if (estimatedSeconds < 3600) {
            return `About ${Math.round(estimatedSeconds / 60)} minutes`;
        } else {
            const hours = Math.floor(estimatedSeconds / 3600);
            const minutes = Math.round((estimatedSeconds % 3600) / 60);
            return `About ${hours} hour${hours !== 1 ? 's' : ''} ${minutes} minute${minutes !== 1 ? 's' : ''}`;
        }
    }
    
    // Check task status
    function checkStatus() {
        if (!currentTaskId) return;
        
        fetch(`/status/${currentTaskId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Status response:', data);
                
                if (!data.success) {
                    clearInterval(statusCheckInterval);
                    showError(data.error || 'Failed to check status');
                    return;
                }
                
                // Update progress bar
                const progress = data.progress || 0;
                downloadProgress.style.width = `${progress}%`;
                processProgress.style.width = `${progress}%`;
                percentageText.textContent = `${progress}%`;
                
                // Update status based on task state
                const status = data.status;
                let statusMessage = capitalizeFirstLetter(status);
                
                // Add stage information if available
                if (data.current_stage) {
                    statusMessage += `: ${data.current_stage}`;
                }
                statusText.textContent = statusMessage;
                
                // Update estimated time if progress changed
                if (progress > lastProgress) {
                    const estimatedTime = calculateEstimatedTime(progress);
                    estimatedTimeEl.textContent = estimatedTime;
                    lastProgress = progress;
                }
                
                if (status === 'completed') {
                    clearInterval(statusCheckInterval);
                    
                    // Show download section
                    downloadSection.style.display = 'block';
                    estimatedTimeEl.textContent = 'Complete!';
                    
                    // Set download link and file path
                    if (data.file_path) {
                        fileLocation.style.display = 'block';
                        filePath.textContent = data.file_path;
                        
                        // Set download link if a download URL is provided
                        if (data.download_url) {
                            downloadLink.href = data.download_url;
                        }
                    }
                    
                    // Reset form
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Create Short';
                    
                    showToast('Video processing complete!', 'success');
                } 
                else if (status === 'failed') {
                    clearInterval(statusCheckInterval);
                    showError(data.error || 'Processing failed');
                    estimatedTimeEl.textContent = 'Failed';
                    
                    // Reset form
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Create Short';
                }
            })
            .catch(error => {
                console.error('Status check error:', error);
                clearInterval(statusCheckInterval);
                showError('Failed to check status: ' + error.message);
                
                // Reset form
                submitBtn.disabled = false;
                submitBtn.textContent = 'Create Short';
            });
    }
    
    // Show error message
    function showError(message) {
        errorSection.style.display = 'block';
        errorText.textContent = message;
        showToast(message, 'error');
    }
    
    // Reset progress UI
    function resetProgressUI() {
        downloadProgress.style.width = '0%';
        processProgress.style.width = '0%';
        percentageText.textContent = '0%';
        statusText.textContent = 'Initializing...';
        estimatedTimeEl.textContent = 'Calculating...';
        downloadSection.style.display = 'none';
        errorSection.style.display = 'none';
        fileLocation.style.display = 'none';
    }
    
    // Try again button
    retryBtn.addEventListener('click', function() {
        progressContainer.style.display = 'none';
        videoInput.style.display = 'block';
    });
    
    // Create another video button
    newVideoBtn.addEventListener('click', function() {
        progressContainer.style.display = 'none';
        videoInput.style.display = 'block';
        youtubeUrlInput.value = '';
        resetProgressUI();
    });
    
    // Helper function to capitalize first letter
    function capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }
    
    // Submit video URL to server
    function submitVideo(url, duration, format, outputPath, captions) {
        // Reset progress tracking
        resetProgressUI();
        
        // Log values for debugging
        console.log('Submitting video with values:');
        console.log('URL:', url);
        console.log('Duration:', duration);
        console.log('Format:', format);
        console.log('Output path:', outputPath);
        console.log('Captions:', captions);
        
        // Create form data with the exact field names the server expects
        const formData = new FormData();
        
        // These field names MUST match what the Flask backend expects in app.py
        formData.append('url', url);
        formData.append('duration', duration);
        formData.append('format', format);
        formData.append('output_path', outputPath);
        formData.append('captions', captions ? 'true' : 'false');
        
        // Log FormData entries for debugging
        console.log('FormData entries:');
        for (let [key, value] of formData.entries()) {
            console.log(`${key}: ${value}`);
        }
        
        // Setting proper content type for the fetch request
        fetch('/process', {
            method: 'POST',
            body: formData,
            // Don't set Content-Type header, let the browser set it with boundary parameter
        })
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Response data:', data);
            if (data.success) {
                currentTaskId = data.task_id;
                // Start checking status
                statusCheckInterval = setInterval(checkStatus, 1000);
            } else {
                showError(data.error || 'Failed to process video');
            }
        })
        .catch(error => {
            console.error('Fetch error:', error);
            showError('Server error: ' + error.message);
        });
    }
    
    // Show toast notification
    function showToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }
}); 