//function getId() {
//  document.querySelector('.name-user').innerHTML = document.getElementById("name-user").name;
//  document.querySelector('.surname-user').innerHTML = document.getElementById("surname-user").name;
//  document.querySelector('.email-user').innerHTML = document.getElementById("email-user").name;
//  document.querySelector('.level-user').innerHTML = document.getElementById("level-user").name;
//  document.querySelector('.date-user').innerHTML = document.getElementById("date-user").name;
//}
//
//// Открыть модальное окно
//document.getElementById("modal-user-profile").addEventListener("click", function() {
//    document.getElementById("modal-box").classList.add("open");
//})
//
//// Закрыть модальное окно
//document.getElementById("user-profile-close").addEventListener("click", function() {
//    document.getElementById("modal-box").classList.remove("open");
//})
//
//// Закрыть модальное окно при клике вне его
//document.querySelector("#modal-box .user-profile").addEventListener('click', event => {
//    event._isClickWithInModal = true;
//});
//document.getElementById("modal-box").addEventListener('click', event => {
//    if (event._isClickWithInModal) return;
//    event.currentTarget.classList.remove('open');
//});

//document.body.addEventListener("click", function(event) {
//    event.preventDefault();
//
//    document.getElementById("show-profile").submit();
//});



document.body.onclick = function(e) {
//    alert(e.target.classList);
    if(e.target.classList.contains('btn-send')){
        alert(e.target.classList);
//        document.getElementById('comment').reset();
    }
    if(e.target.classList.contains('link')){
    document.getElementById("show-profile").submit();
    }
}

//function ClearField {
//    document.getElementById('comment').reset();
//}
