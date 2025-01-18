// Masq msg flash apre sec
function hideFlashMessages() {
    const flashMessages = document.getElementById('flash-messages');
    if (flashMessages) {
        flashMessages.querySelectorAll('.flash-message').forEach(message => {
            message.classList.add('fade-out');
        });

        setTimeout(() => {
            flashMessages.remove();
        }, 1000); 
    }
}

setTimeout(hideFlashMessages, 4000);