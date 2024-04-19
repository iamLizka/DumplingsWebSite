
// Открыть модальное окно
document.getElementById("modal-user-profile").addEventListener("click", function() {
    document.getElementById("modal-box").classList.add("open")
})

// Закрыть модальное окно
document.getElementById("user-profile-close").addEventListener("click", function() {
    document.getElementById("modal-box").classList.remove("open")
})

// Закрыть модальное окно при клике вне его
document.querySelector("#modal-box .user-profile").addEventListener('click', event => {
    event._isClickWithInModal = true;
});
document.getElementById("modal-box").addEventListener('click', event => {
    if (event._isClickWithInModal) return;
    event.currentTarget.classList.remove('open');
});